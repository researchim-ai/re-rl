#!/usr/bin/env python3
"""
Извлечение теорем с доказательствами из traced Mathlib4.

Напрямую читает .ast.json файлы и извлекает:
  - (stateBefore, tactic, stateAfter) — training pairs
  - theorem_name, module, full proof sequence

Это НАМНОГО быстрее чем BFS и даёт реальные многошаговые доказательства.

Использование:
    # Базовый запуск — все теоремы
    python examples/extract_mathlib_proofs.py

    # Ограничить количество
    python examples/extract_mathlib_proofs.py --max-theorems 10000

    # Только определённые модули
    python examples/extract_mathlib_proofs.py --module-prefix Mathlib.Algebra

    # Минимальная длина доказательства (многошаговые)
    python examples/extract_mathlib_proofs.py --min-proof-length 3

    # Разные форматы вывода
    python examples/extract_mathlib_proofs.py --output-format chat

Предварительно нужен трейсинг:
    python scripts/fast_trace.py --version v4.26.0
"""

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):
        return iterable


def parse_args():
    parser = argparse.ArgumentParser(
        description="Извлечение теорем с доказательствами из traced Mathlib4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python examples/extract_mathlib_proofs.py                    # все теоремы
  python examples/extract_mathlib_proofs.py --max-theorems 5000
  python examples/extract_mathlib_proofs.py --min-proof-length 3  # многошаговые
  python examples/extract_mathlib_proofs.py --module-prefix Mathlib.Algebra
        """,
    )
    parser.add_argument("--mathlib-version", default="v4.26.0",
                        help="Версия Mathlib4 (default: v4.26.0)")
    parser.add_argument("--max-theorems", type=int, default=0,
                        help="Макс теорем (0 = все, default: 0)")
    parser.add_argument("--max-files", type=int, default=0,
                        help="Макс AST файлов (0 = все, default: 0)")
    parser.add_argument("--min-proof-length", type=int, default=1,
                        help="Мин количество тактик в доказательстве (default: 1)")
    parser.add_argument("--max-proof-length", type=int, default=50,
                        help="Макс количество тактик (default: 50)")
    parser.add_argument("--module-prefix", default="",
                        help="Фильтр по префиксу модуля (e.g., Mathlib.Algebra)")
    parser.add_argument("--output-dir", default=None,
                        help="Директория для результатов")
    parser.add_argument("--output-format", default="jsonl",
                        choices=["jsonl", "json", "sft", "chat"],
                        help="Формат датасета (default: jsonl)")
    parser.add_argument("--include-state-after", action="store_true",
                        help="Включать stateAfter в пары")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed для shuffle")
    parser.add_argument("--skip-packages", action="store_true", default=True,
                        help="Пропускать зависимости (default: True)")
    parser.add_argument("--verbose", action="store_true",
                        help="Подробный вывод")
    return parser.parse_args()


def extract_tactic_text(source_bytes: bytes, pos, end_pos) -> str:
    """Извлекает текст тактики из исходного кода по позициям.
    
    pos/end_pos могут быть:
      - int (byte offsets) — новый формат
      - dict с line/column — старый формат
    """
    try:
        # Новый формат: byte offsets
        if isinstance(pos, int) and isinstance(end_pos, int):
            return source_bytes[pos:end_pos].decode('utf-8', errors='replace')
        
        # Старый формат: line/column
        if isinstance(pos, dict) and isinstance(end_pos, dict):
            lines = source_bytes.split(b'\n')
            start_line = pos.get("line", 1) - 1
            start_col = pos.get("column", 0)
            end_line = end_pos.get("line", 1) - 1
            end_col = end_pos.get("column", 0)
            
            if start_line == end_line:
                return lines[start_line][start_col:end_col].decode('utf-8', errors='replace')
            else:
                result = [lines[start_line][start_col:]]
                for i in range(start_line + 1, end_line):
                    result.append(lines[i])
                result.append(lines[end_line][:end_col])
                return b'\n'.join(result).decode('utf-8', errors='replace')
        
        return ""
    except Exception:
        return ""


def extract_theorems_from_ast(
    ast_file: Path,
    lean_file: Path,
    module_name: str,
    min_proof_length: int = 1,
    max_proof_length: int = 50,
) -> List[Dict]:
    """
    Извлекает теоремы с доказательствами из одного AST файла.
    
    Returns:
        Список словарей с ключами:
        - theorem_name: имя теоремы (или module.anonymous_N)
        - module: имя модуля
        - goal_state: начальное состояние (stateBefore первой тактики)
        - tactics: список {stateBefore, stateAfter, tactic_text}
        - proof_length: количество тактик
    """
    theorems = []
    
    try:
        with open(ast_file) as f:
            data = json.load(f)
    except Exception:
        return []
    
    tactics_data = data.get("tactics", [])
    if not tactics_data:
        return []
    
    # Читаем исходный код для извлечения текста тактик
    try:
        source_bytes = lean_file.read_bytes()
    except Exception:
        source_bytes = b""
    
    # Группируем тактики по начальному состоянию (каждая группа = одна теорема/лемма)
    # Эвристика: новая теорема начинается когда stateBefore содержит только "⊢" (goal без гипотез)
    # или когда stateBefore сильно отличается от предыдущего stateAfter
    
    current_theorem_tactics = []
    current_theorem_name = f"{module_name}.anonymous_0"
    theorem_counter = 0
    
    for i, tac in enumerate(tactics_data):
        state_before = tac.get("stateBefore", "")
        state_after = tac.get("stateAfter", "")
        pos = tac.get("pos", {})
        end_pos = tac.get("endPos", {})
        
        # Извлекаем текст тактики
        tactic_text = extract_tactic_text(source_bytes, pos, end_pos)
        if not tactic_text:
            tactic_text = tac.get("tactic", "")  # fallback
        
        # Определяем начало новой теоремы
        is_new_theorem = False
        if i == 0:
            is_new_theorem = True
        elif current_theorem_tactics:
            # Если предыдущий stateAfter пустой (доказательство завершено)
            prev_after = current_theorem_tactics[-1].get("stateAfter", "")
            if not prev_after.strip() or prev_after == "no goals":
                is_new_theorem = True
            # Или если текущий stateBefore совсем не связан с предыдущим
            elif state_before and prev_after and state_before != prev_after:
                # Проверяем — это новая теорема или продолжение?
                # Новая теорема обычно начинается с чистого goal без гипотез из прошлого
                if "⊢" in state_before:
                    lines = state_before.strip().split('\n')
                    # Если первая строка — goal (⊢), это может быть новая теорема
                    if lines and lines[0].strip().startswith("⊢"):
                        is_new_theorem = True
        
        if is_new_theorem and current_theorem_tactics:
            # Сохраняем предыдущую теорему
            proof_len = len(current_theorem_tactics)
            if min_proof_length <= proof_len <= max_proof_length:
                theorems.append({
                    "theorem_name": current_theorem_name,
                    "module": module_name,
                    "goal_state": current_theorem_tactics[0]["stateBefore"],
                    "tactics": current_theorem_tactics,
                    "proof_length": proof_len,
                })
            
            theorem_counter += 1
            current_theorem_name = f"{module_name}.anonymous_{theorem_counter}"
            current_theorem_tactics = []
        
        current_theorem_tactics.append({
            "stateBefore": state_before,
            "stateAfter": state_after,
            "tactic_text": tactic_text.strip(),
        })
    
    # Последняя теорема
    if current_theorem_tactics:
        proof_len = len(current_theorem_tactics)
        if min_proof_length <= proof_len <= max_proof_length:
            theorems.append({
                "theorem_name": current_theorem_name,
                "module": module_name,
                "goal_state": current_theorem_tactics[0]["stateBefore"],
                "tactics": current_theorem_tactics,
                "proof_length": proof_len,
            })
    
    return theorems


def theorems_to_pairs(theorems: List[Dict], include_state_after: bool = False) -> List[Dict]:
    """Конвертирует теоремы в training pairs (state, tactic).
    
    Каждая пара включает:
    - state: текущее состояние доказательства
    - tactic: следующая тактика
    - theorem_name: имя теоремы
    - theorem_statement: исходная формулировка (goal_state) — для контекста в SFT
    - distance_to_proof: шагов до завершения
    """
    pairs = []
    
    for thm in theorems:
        theorem_name = thm["theorem_name"]
        tactics = thm["tactics"]
        proof_length = len(tactics)
        # goal_state — исходная формулировка теоремы (первый stateBefore)
        theorem_statement = thm.get("goal_state", "")
        
        for i, tac in enumerate(tactics):
            pair = {
                "state": tac["stateBefore"],
                "tactic": tac["tactic_text"],
                "theorem_name": theorem_name,
                "theorem_statement": theorem_statement,  # ← контекст для SFT
                "distance_to_proof": proof_length - i,  # шагов до конца
                "step_index": i,
                "proof_length": proof_length,
            }
            if include_state_after:
                pair["next_state"] = tac["stateAfter"]
            pairs.append(pair)
    
    return pairs


def save_dataset(pairs: List[Dict], theorems: List[Dict], 
                 output_dir: Path, fmt: str, metadata: Dict):
    """Сохраняет датасет в указанном формате."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if fmt == "jsonl":
        f = output_dir / f"mathlib_proofs_{ts}.jsonl"
        with open(f, "w") as fh:
            for p in pairs:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    elif fmt == "json":
        f = output_dir / f"mathlib_proofs_{ts}.json"
        with open(f, "w") as fh:
            json.dump(pairs, fh, indent=2, ensure_ascii=False)
    elif fmt == "sft":
        f = output_dir / f"mathlib_sft_{ts}.json"
        sft = [{
            "instruction": "You are a Lean 4 theorem prover. Given the proof state, output the next tactic.",
            "input": f"Proof state:\n{p['state']}",
            "output": p["tactic"],
        } for p in pairs if p["tactic"]]
        with open(f, "w") as fh:
            json.dump(sft, fh, indent=2, ensure_ascii=False)
    elif fmt == "chat":
        f = output_dir / f"mathlib_chat_{ts}.json"
        chat = [{
            "messages": [
                {"role": "system", "content": "You are an expert Lean 4 theorem prover. Given the current proof state, provide the next tactic."},
                {"role": "user", "content": f"Current proof state:\n```\n{p['state']}\n```\n\nWhat tactic should I apply?"},
                {"role": "assistant", "content": p["tactic"]},
            ]
        } for p in pairs if p["tactic"]]
        with open(f, "w") as fh:
            json.dump(chat, fh, indent=2, ensure_ascii=False)
    
    # Сохраняем также полные теоремы
    thm_file = output_dir / f"mathlib_theorems_{ts}.json"
    with open(thm_file, "w") as fh:
        json.dump(theorems, fh, indent=2, ensure_ascii=False)
    
    # Метаданные
    mf = output_dir / f"metadata_{ts}.json"
    with open(mf, "w") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n  Training pairs: {f}  ({f.stat().st_size:,} bytes)")
    print(f"  Full theorems:  {thm_file}  ({thm_file.stat().st_size:,} bytes)")
    print(f"  Metadata:       {mf}")
    
    return f


def main():
    args = parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    # Пути
    CACHE_BASE = Path.home() / ".cache" / "re_rl"
    REPO_DIR = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "mathlib4"
    OUTPUT_DIR = Path(args.output_dir) if args.output_dir else Path("datasets/mathlib_proofs")
    
    print("=" * 60)
    print("  ИЗВЛЕЧЕНИЕ ТЕОРЕМ ИЗ MATHLIB4")
    print("=" * 60)
    print(f"  Mathlib:           {args.mathlib_version}")
    print(f"  Repo:              {REPO_DIR}")
    print(f"  Min proof length:  {args.min_proof_length}")
    print(f"  Max proof length:  {args.max_proof_length}")
    if args.module_prefix:
        print(f"  Module prefix:     {args.module_prefix}")
    print(f"  Output:            {OUTPUT_DIR}")
    print(f"  Format:            {args.output_format}")
    print()
    
    # Проверка трейсинга
    if not (REPO_DIR.parent / ".step_5_done").exists():
        print(f"ОШИБКА: Трейсинг не выполнен для {args.mathlib_version}")
        print(f"  Запустите: python scripts/fast_trace.py --version {args.mathlib_version}")
        sys.exit(1)
    
    build_ir = REPO_DIR / ".lake" / "build" / "ir"
    if not build_ir.exists():
        print(f"ОШИБКА: Нет директории {build_ir}")
        sys.exit(1)
    
    # Собираем AST файлы
    ast_files = sorted(build_ir.rglob("*.ast.json"))
    
    if args.skip_packages:
        ast_files = [f for f in ast_files 
                     if "packages" not in str(f.relative_to(build_ir))]
    
    if args.module_prefix:
        # Фильтр по модулю: Mathlib.Algebra → Mathlib/Algebra/
        prefix_path = args.module_prefix.replace(".", "/")
        ast_files = [f for f in ast_files 
                     if prefix_path in str(f.relative_to(build_ir))]
    
    if args.max_files > 0 and len(ast_files) > args.max_files:
        ast_files = random.sample(ast_files, args.max_files)
    
    print(f"AST файлов: {len(ast_files)}")
    print()
    
    # Извлекаем теоремы
    all_theorems = []
    files_with_theorems = 0
    
    iterator = tqdm(ast_files, desc="Извлечение") if TQDM_AVAILABLE else ast_files
    
    for ast_file in iterator:
        # Определяем путь к .lean файлу
        rel = ast_file.relative_to(build_ir)
        module_name = str(rel).replace(".ast.json", "").replace("/", ".")
        lean_rel = Path(str(rel).replace(".ast.json", ".lean"))
        lean_file = REPO_DIR / lean_rel
        
        if not lean_file.exists():
            continue
        
        theorems = extract_theorems_from_ast(
            ast_file, lean_file, module_name,
            min_proof_length=args.min_proof_length,
            max_proof_length=args.max_proof_length,
        )
        
        if theorems:
            files_with_theorems += 1
            all_theorems.extend(theorems)
        
        # Ограничение по теоремам
        if args.max_theorems > 0 and len(all_theorems) >= args.max_theorems:
            all_theorems = all_theorems[:args.max_theorems]
            break
    
    print(f"\nИзвлечено: {len(all_theorems)} теорем из {files_with_theorems} файлов")
    
    if not all_theorems:
        print("Нет теорем для сохранения.")
        sys.exit(0)
    
    # Статистика
    proof_lengths = [t["proof_length"] for t in all_theorems]
    print(f"\n{'='*60}")
    print(f"  СТАТИСТИКА")
    print(f"{'='*60}")
    print(f"  Теорем:              {len(all_theorems)}")
    print(f"  Средняя длина proof: {sum(proof_lengths)/len(proof_lengths):.1f}")
    print(f"  Мин/Макс длина:      {min(proof_lengths)} / {max(proof_lengths)}")
    
    # Распределение длин
    length_dist = defaultdict(int)
    for l in proof_lengths:
        length_dist[l] += 1
    
    print(f"\n  Распределение длин доказательств:")
    for l in sorted(length_dist.keys())[:15]:
        print(f"    {l:3d} тактик: {length_dist[l]:6d} теорем")
    if len(length_dist) > 15:
        print(f"    ... и ещё {len(length_dist) - 15} длин")
    
    # Конвертируем в pairs
    pairs = theorems_to_pairs(all_theorems, include_state_after=args.include_state_after)
    print(f"\n  Training pairs:      {len(pairs)}")
    
    # Топ тактики
    tactic_counts = defaultdict(int)
    for p in pairs:
        base_tac = p["tactic"].split()[0] if p["tactic"] else ""
        tactic_counts[base_tac] += 1
    
    print(f"\n  Топ-15 тактик:")
    for tac, cnt in sorted(tactic_counts.items(), key=lambda x: -x[1])[:15]:
        pct = 100 * cnt / len(pairs)
        print(f"    {tac:25s} {cnt:6d} ({pct:.1f}%)")
    
    # Сохранение
    print(f"\n{'='*60}")
    print(f"  СОХРАНЕНИЕ")
    print(f"{'='*60}")
    
    metadata = {
        "mathlib_version": args.mathlib_version,
        "extraction_date": datetime.now().isoformat(),
        "config": {
            "min_proof_length": args.min_proof_length,
            "max_proof_length": args.max_proof_length,
            "module_prefix": args.module_prefix,
            "max_theorems": args.max_theorems,
            "max_files": args.max_files,
        },
        "summary": {
            "total_theorems": len(all_theorems),
            "total_pairs": len(pairs),
            "files_processed": files_with_theorems,
            "avg_proof_length": sum(proof_lengths) / len(proof_lengths),
        },
    }
    
    save_dataset(pairs, all_theorems, OUTPUT_DIR, args.output_format, metadata)
    
    print(f"\nГотово! {len(pairs)} training pairs из {len(all_theorems)} теорем.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
