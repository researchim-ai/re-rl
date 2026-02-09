#!/usr/bin/env python3
"""
Извлечение данных из Mathlib4 для pretraining.

Генерирует разные виды данных:
  1. lean_code    — сырой Lean код (для изучения синтаксиса)
  2. theorems     — формулировки теорем (statement без proof)
  3. definitions  — определения (def, structure, class, inductive)
  4. docstrings   — документация к теоремам/определениям
  5. proofs       — теоремы с доказательствами (theorem + proof)

Использование:
    # Всё вместе
    python examples/formal/extract_lean_pretrain.py --all

    # Только теоремы (statements)
    python examples/formal/extract_lean_pretrain.py --theorems --max-files 1000

    # Lean код для language modeling
    python examples/formal/extract_lean_pretrain.py --lean-code --chunk-size 2048

    # Определения и docstrings
    python examples/formal/extract_lean_pretrain.py --definitions --docstrings
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    def tqdm(iterable, **kwargs):
        return iterable


def parse_args():
    parser = argparse.ArgumentParser(
        description="Извлечение данных из Mathlib4 для pretraining",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mathlib-version", default="v4.26.0",
                        help="Версия Mathlib4 (default: v4.26.0)")
    parser.add_argument("--output-dir", default="datasets/lean_pretrain",
                        help="Директория для результатов")
    
    # Типы данных
    parser.add_argument("--all", action="store_true",
                        help="Извлечь все типы данных")
    parser.add_argument("--lean-code", action="store_true",
                        help="Сырой Lean код (для LM pretraining)")
    parser.add_argument("--theorems", action="store_true",
                        help="Формулировки теорем (statements)")
    parser.add_argument("--definitions", action="store_true",
                        help="Определения (def, structure, class)")
    parser.add_argument("--docstrings", action="store_true",
                        help="Документация к теоремам")
    parser.add_argument("--proofs", action="store_true",
                        help="Теоремы с доказательствами")
    
    # Параметры
    parser.add_argument("--max-files", type=int, default=0,
                        help="Макс файлов (0 = все)")
    parser.add_argument("--chunk-size", type=int, default=4096,
                        help="Размер чанка для lean-code (в символах)")
    parser.add_argument("--module-prefix", default="",
                        help="Фильтр по модулю (e.g., Mathlib.Algebra)")
    parser.add_argument("--skip-imports", action="store_true",
                        help="Пропускать import секции")
    parser.add_argument("--min-length", type=int, default=50,
                        help="Мин длина текста (символов)")
    
    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════
#  ПАРСИНГ LEAN КОДА
# ═══════════════════════════════════════════════════════════════

# Регулярки для извлечения элементов Lean
THEOREM_PATTERN = re.compile(
    r'^(theorem|lemma)\s+(\S+)\s*(.*?)(?=^(?:theorem|lemma|def|structure|class|inductive|instance|example|#|end|namespace|\Z))',
    re.MULTILINE | re.DOTALL
)

DEFINITION_PATTERN = re.compile(
    r'^(def|abbrev|structure|class|inductive|instance)\s+(\S+)\s*(.*?)(?=^(?:theorem|lemma|def|structure|class|inductive|instance|example|#|end|namespace|\Z))',
    re.MULTILINE | re.DOTALL
)

DOCSTRING_PATTERN = re.compile(
    r'/--\s*(.*?)\s*-/',
    re.DOTALL
)

STATEMENT_PATTERN = re.compile(
    r'^(theorem|lemma)\s+(\S+)\s*([^:]*:\s*[^:=]+)',
    re.MULTILINE
)


def extract_theorems_from_lean(content: str, module: str) -> List[Dict]:
    """Извлекает формулировки теорем (без доказательств)."""
    theorems = []
    
    for match in STATEMENT_PATTERN.finditer(content):
        kind = match.group(1)  # theorem/lemma
        name = match.group(2)
        signature = match.group(3).strip()
        
        # Убираем where и доказательство
        if ":=" in signature:
            signature = signature.split(":=")[0].strip()
        if " where" in signature:
            signature = signature.split(" where")[0].strip()
        
        # Полное имя
        full_name = f"{module}.{name}" if module else name
        
        theorems.append({
            "type": kind,
            "name": full_name,
            "statement": f"{kind} {name} {signature}",
            "module": module,
        })
    
    return theorems


def extract_definitions_from_lean(content: str, module: str) -> List[Dict]:
    """Извлекает определения (def, structure, class, etc.)."""
    definitions = []
    
    for match in DEFINITION_PATTERN.finditer(content):
        kind = match.group(1)
        name = match.group(2)
        body = match.group(3).strip()
        
        # Ограничиваем длину
        if len(body) > 5000:
            body = body[:5000] + "\n-- [truncated]"
        
        full_name = f"{module}.{name}" if module else name
        full_text = f"{kind} {name} {body}"
        
        definitions.append({
            "type": kind,
            "name": full_name,
            "definition": full_text,
            "module": module,
        })
    
    return definitions


def extract_docstrings(content: str, module: str) -> List[Dict]:
    """Извлекает docstrings с контекстом."""
    docstrings = []
    
    # Находим docstrings и следующий за ними элемент
    for match in DOCSTRING_PATTERN.finditer(content):
        doc_text = match.group(1).strip()
        end_pos = match.end()
        
        # Ищем следующий элемент после docstring
        after = content[end_pos:end_pos + 500]
        
        # Определяем что документируется
        elem_match = re.match(
            r'\s*(theorem|lemma|def|structure|class|instance)\s+(\S+)',
            after
        )
        
        if elem_match:
            elem_type = elem_match.group(1)
            elem_name = elem_match.group(2)
            full_name = f"{module}.{elem_name}" if module else elem_name
            
            docstrings.append({
                "name": full_name,
                "type": elem_type,
                "docstring": doc_text,
                "module": module,
            })
    
    return docstrings


def extract_proofs_from_lean(content: str, module: str) -> List[Dict]:
    """Извлекает теоремы с доказательствами."""
    proofs = []
    
    for match in THEOREM_PATTERN.finditer(content):
        kind = match.group(1)
        name = match.group(2)
        body = match.group(3).strip()
        
        # Пропускаем если нет доказательства
        if ":=" not in body and "by" not in body:
            continue
        
        # Ограничиваем длину
        if len(body) > 10000:
            body = body[:10000] + "\n-- [truncated]"
        
        full_name = f"{module}.{name}" if module else name
        full_text = f"{kind} {name} {body}"
        
        proofs.append({
            "type": kind,
            "name": full_name,
            "proof": full_text,
            "module": module,
        })
    
    return proofs


def chunk_lean_code(content: str, chunk_size: int, skip_imports: bool = False) -> List[str]:
    """Разбивает Lean код на чанки для LM pretraining."""
    if skip_imports:
        # Убираем import секцию
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('import'):
                start_idx = i
                break
        content = '\n'.join(lines[start_idx:])
    
    chunks = []
    
    # Разбиваем по границам определений/теорем где возможно
    # Простой подход: по chunk_size с выравниванием на конец строки
    pos = 0
    while pos < len(content):
        end = min(pos + chunk_size, len(content))
        
        # Ищем конец строки для ровного разреза
        if end < len(content):
            newline = content.rfind('\n', pos, end)
            if newline > pos:
                end = newline + 1
        
        chunk = content[pos:end].strip()
        if chunk:
            chunks.append(chunk)
        
        pos = end
    
    return chunks


# ═══════════════════════════════════════════════════════════════
#  ОСНОВНАЯ ЛОГИКА
# ═══════════════════════════════════════════════════════════════

def process_lean_files(
    repo_dir: Path,
    max_files: int = 0,
    module_prefix: str = "",
    extract_types: set = None,
    chunk_size: int = 4096,
    skip_imports: bool = False,
    min_length: int = 50,
) -> Dict[str, List]:
    """Обрабатывает .lean файлы и извлекает данные."""
    
    results = {
        "lean_code": [],
        "theorems": [],
        "definitions": [],
        "docstrings": [],
        "proofs": [],
    }
    
    # Собираем .lean файлы
    lean_files = sorted(repo_dir.rglob("*.lean"))
    
    # Фильтруем packages
    lean_files = [f for f in lean_files if ".lake/packages" not in str(f)]
    
    # Фильтр по модулю
    if module_prefix:
        prefix_path = module_prefix.replace(".", "/")
        lean_files = [f for f in lean_files if prefix_path in str(f)]
    
    # Ограничение
    if max_files > 0 and len(lean_files) > max_files:
        lean_files = lean_files[:max_files]
    
    print(f"Обработка {len(lean_files)} .lean файлов...")
    
    iterator = tqdm(lean_files, desc="Извлечение") if TQDM_AVAILABLE else lean_files
    
    for lean_file in iterator:
        try:
            content = lean_file.read_text(encoding='utf-8', errors='replace')
        except Exception:
            continue
        
        if len(content) < min_length:
            continue
        
        # Определяем имя модуля
        try:
            rel = lean_file.relative_to(repo_dir)
            module = str(rel).replace(".lean", "").replace("/", ".")
        except ValueError:
            module = lean_file.stem
        
        # Извлекаем данные по типам
        if "lean_code" in extract_types:
            chunks = chunk_lean_code(content, chunk_size, skip_imports)
            for i, chunk in enumerate(chunks):
                if len(chunk) >= min_length:
                    results["lean_code"].append({
                        "text": chunk,
                        "module": module,
                        "chunk_idx": i,
                        "source": str(lean_file.name),
                    })
        
        if "theorems" in extract_types:
            theorems = extract_theorems_from_lean(content, module)
            results["theorems"].extend(theorems)
        
        if "definitions" in extract_types:
            defs = extract_definitions_from_lean(content, module)
            results["definitions"].extend(defs)
        
        if "docstrings" in extract_types:
            docs = extract_docstrings(content, module)
            results["docstrings"].extend(docs)
        
        if "proofs" in extract_types:
            proofs = extract_proofs_from_lean(content, module)
            results["proofs"].extend(proofs)
    
    return results


def save_results(results: Dict[str, List], output_dir: Path, metadata: Dict):
    """Сохраняет результаты."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    saved_files = []
    
    for data_type, items in results.items():
        if not items:
            continue
        
        filename = output_dir / f"{data_type}_{ts}.jsonl"
        with open(filename, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        
        saved_files.append((data_type, filename, len(items)))
        print(f"  {data_type}: {filename.name} ({len(items):,} записей, {filename.stat().st_size:,} bytes)")
    
    # Метаданные
    meta_file = output_dir / f"metadata_{ts}.json"
    metadata["files"] = {t: str(f) for t, f, _ in saved_files}
    metadata["counts"] = {t: c for t, _, c in saved_files}
    
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"  metadata: {meta_file.name}")
    
    return saved_files


def main():
    args = parse_args()
    
    # Определяем что извлекать
    extract_types = set()
    if args.all:
        extract_types = {"lean_code", "theorems", "definitions", "docstrings", "proofs"}
    else:
        if args.lean_code:
            extract_types.add("lean_code")
        if args.theorems:
            extract_types.add("theorems")
        if args.definitions:
            extract_types.add("definitions")
        if args.docstrings:
            extract_types.add("docstrings")
        if args.proofs:
            extract_types.add("proofs")
    
    if not extract_types:
        print("Укажите тип данных: --all, --lean-code, --theorems, --definitions, --docstrings, --proofs")
        print("Используйте --help для справки.")
        sys.exit(1)
    
    # Пути
    CACHE_BASE = Path.home() / ".cache" / "re_rl"
    REPO_DIR = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "mathlib4"
    OUTPUT_DIR = Path(args.output_dir)
    
    print("=" * 60)
    print("  ИЗВЛЕЧЕНИЕ ДАННЫХ ДЛЯ PRETRAINING")
    print("=" * 60)
    print(f"  Mathlib:      {args.mathlib_version}")
    print(f"  Repo:         {REPO_DIR}")
    print(f"  Типы данных:  {sorted(extract_types)}")
    print(f"  Output:       {OUTPUT_DIR}")
    if args.module_prefix:
        print(f"  Модуль:       {args.module_prefix}")
    print()
    
    # Проверка
    if not REPO_DIR.exists():
        print(f"ОШИБКА: Репозиторий не найден: {REPO_DIR}")
        print(f"  Запустите: python scripts/fast_trace.py --version {args.mathlib_version}")
        sys.exit(1)
    
    # Извлечение
    results = process_lean_files(
        repo_dir=REPO_DIR,
        max_files=args.max_files,
        module_prefix=args.module_prefix,
        extract_types=extract_types,
        chunk_size=args.chunk_size,
        skip_imports=args.skip_imports,
        min_length=args.min_length,
    )
    
    # Статистика
    print(f"\n{'='*60}")
    print("  СТАТИСТИКА")
    print("=" * 60)
    
    total = 0
    for data_type, items in results.items():
        if items:
            print(f"  {data_type:15s}: {len(items):,}")
            total += len(items)
    print(f"  {'─'*30}")
    print(f"  {'ВСЕГО':15s}: {total:,}")
    
    if total == 0:
        print("\nНет данных для сохранения.")
        sys.exit(0)
    
    # Сохранение
    print(f"\n{'='*60}")
    print("  СОХРАНЕНИЕ")
    print("=" * 60)
    
    metadata = {
        "mathlib_version": args.mathlib_version,
        "extraction_date": datetime.now().isoformat(),
        "config": {
            "max_files": args.max_files,
            "module_prefix": args.module_prefix,
            "chunk_size": args.chunk_size,
            "skip_imports": args.skip_imports,
            "min_length": args.min_length,
            "extract_types": list(extract_types),
        },
    }
    
    save_results(results, OUTPUT_DIR, metadata)
    
    print(f"\nГотово! {total:,} записей для pretraining.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
