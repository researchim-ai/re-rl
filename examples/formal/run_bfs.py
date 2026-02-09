#!/usr/bin/env python3
"""
BFS exploration теорем Lean 4 через Pantograph.
Генерирует training pairs для обучения LLM theorem proving.

Точная копия pipeline из Formal_Math_Generation.ipynb — в виде скрипта.

Использование:
    # Базовый запуск (50 теорем, 5000 шагов, 60с на теорему)
    python examples/run_bfs.py

    # Быстрый тест
    python examples/run_bfs.py --max-theorems 5 --max-steps 3000 --max-time 15

    # Полный прогон
    python examples/run_bfs.py --max-theorems 500 --max-steps 50000 --max-time 300

    # С подробным выводом
    python examples/run_bfs.py --max-theorems 10 --verbose

Предварительно нужен трейсинг Mathlib:
    python scripts/fast_trace.py --version v4.26.0
"""

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="BFS exploration теорем Lean 4 → training pairs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python examples/run_bfs.py --max-theorems 5 --verbose     # быстрый тест
  python examples/run_bfs.py --max-theorems 100              # средний прогон
  python examples/run_bfs.py --max-theorems 0 --max-time 300 # все теоремы
        """,
    )
    parser.add_argument("--mathlib-version", default="v4.26.0",
                        help="Версия Mathlib4 (default: v4.26.0)")
    parser.add_argument("--max-theorems", type=int, default=50,
                        help="Макс теорем для BFS (0 = все из каталога, default: 50)")
    parser.add_argument("--max-steps", type=int, default=5000,
                        help="Макс шагов BFS на теорему (default: 5000)")
    parser.add_argument("--max-time", type=int, default=60,
                        help="Секунд на теорему (default: 60)")
    parser.add_argument("--min-template-freq", type=int, default=3,
                        help="Мин частота шаблона для RAG (default: 3)")
    parser.add_argument("--output-dir", default=None,
                        help="Директория для результатов (default: datasets/formal_math_data)")
    parser.add_argument("--rag-model", default="sbert",
                        help="RAG модель: 'sbert' (pretrained), 'trained' (обученный BERT), "
                             "или путь к модели (default: sbert)")
    parser.add_argument("--output-format", default="jsonl",
                        choices=["jsonl", "json", "sft", "chat"],
                        help="Формат датасета (default: jsonl)")
    parser.add_argument("--verbose", action="store_true",
                        help="Подробный вывод BFS (показывать состояния)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed для воспроизводимости")
    parser.add_argument("--no-per-file", action="store_true",
                        help="Не использовать per-file server (старый способ, менее надёжный)")
    parser.add_argument("--no-early-stop", action="store_true",
                        help="Отключить раннюю остановку (1/3 бюджета). "
                             "Полезно для нетривиальных теорем.")
    parser.add_argument("--bench", default=None,
                        help="JSON файл с бенчмарком теорем (список {name, module, goal_state, goal_expr}). "
                             "Можно ограничить через --max-theorems.")
    parser.add_argument("--ban-tactics", default=None,
                        help="Список забаненных тактик через запятую. BFS не будет "
                             "применять эти тактики, что заставит искать "
                             "многошаговые доказательства. "
                             "Пример: --ban-tactics simp,simp_all,aesop,omega,tauto,decide")
    parser.add_argument("--no-auto", action="store_true",
                        help="Пресет: забанить нуклеарные тактики-упрощатели "
                             "(simp, simp_all, aesop, omega, tauto, decide, norm_num, "
                             "linarith, ring, trivial, simpa, positivity, field_simp). "
                             "Заставляет BFS искать многошаговые доказательства.")
    parser.add_argument("--min-proof-length", type=int, default=0,
                        help="Мин длина доказательства (distance_to_proof). "
                             "Пары с distance < N отфильтровываются из датасета. "
                             "Пример: --min-proof-length 4 оставит только пары, "
                             "где от состояния нужно >= 4 тактик до proof.")
    parser.add_argument("--decompose-auto", action="store_true",
                        help="Декомпозиция automation-тактик (simp, aesop, ...) "
                             "в цепочки индивидуальных rw-шагов. ")
    parser.add_argument("--no-pp-full", action="store_true",
                        help="Отключить полный pretty-print (разрешить ⋯ обрезку). "
                             "По умолчанию pp_full=True — полный вывод без обрезки."
                             "simp? → simp only [l1, l2, l3] → rw [l1]; rw [l2]; rw [l3]. "
                             "Расширяет датасет ~×2-5 содержательными шагами "
                             "с конкретными леммами вместо «магического» simp.")
    return parser.parse_args()


def check_dependencies():
    """Проверяет все зависимости."""
    print("ПРОВЕРКА ЗАВИСИМОСТЕЙ")
    print("=" * 60)
    ok = True

    # elan
    elan = Path.home() / ".elan" / "bin" / "elan"
    if elan.exists():
        print(f"  elan:                  OK")
    else:
        print(f"  elan:                  НЕТ")
        print(f"    → curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh")
        ok = False

    # pantograph
    try:
        import pantograph
        print(f"  pantograph:            OK")
    except ImportError:
        print(f"  pantograph:            НЕТ  →  pip install -r requirements.txt")
        ok = False

    # faiss
    try:
        import faiss
        print(f"  faiss-cpu:             OK")
    except ImportError:
        print(f"  faiss-cpu:             НЕТ  →  pip install faiss-cpu")
        ok = False

    # sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        print(f"  sentence-transformers: OK")
    except ImportError:
        print(f"  sentence-transformers: НЕТ  →  pip install sentence-transformers")
        ok = False

    # re_rl
    try:
        import re_rl
        print(f"  re_rl:                 OK")
    except ImportError:
        print(f"  re_rl:                 НЕТ  →  pip install -e .")
        ok = False

    print()
    return ok


def save_dataset(pairs, output_dir, fmt, metadata):
    """Сохраняет датасет в указанном формате."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    def pair_to_dict(p):
        return {
            "state": p.state,
            "tactic": p.tactic,
            "next_state": p.next_state,
            "distance_to_proof": p.distance_to_proof,
            "theorem_name": p.theorem_name,
            "theorem_statement": getattr(p, 'theorem_statement', ''),
        }

    if fmt == "jsonl":
        f = output_dir / f"lean_data_{ts}.jsonl"
        with open(f, "w") as fh:
            for p in pairs:
                fh.write(json.dumps(pair_to_dict(p), ensure_ascii=False) + "\n")
    elif fmt == "json":
        f = output_dir / f"lean_data_{ts}.json"
        with open(f, "w") as fh:
            json.dump([pair_to_dict(p) for p in pairs], fh, indent=2, ensure_ascii=False)
    elif fmt == "sft":
        f = output_dir / f"lean_sft_{ts}.json"
        sft = []
        for p in pairs:
            # Пропускаем negative examples (пустой tactic)
            if not p.tactic or not p.tactic.strip():
                continue
            thm_stmt = getattr(p, 'theorem_statement', '')
            input_text = f"Theorem to prove: {thm_stmt}\n\nCurrent proof state:\n{p.state}" if thm_stmt else f"Current proof state:\n{p.state}"
            sft.append({
                "instruction": "You are a Lean 4 theorem prover. Given the theorem and current proof state, suggest the next tactic.",
                "input": input_text,
                "output": p.tactic,
            })
        with open(f, "w") as fh:
            json.dump(sft, fh, indent=2, ensure_ascii=False)
    elif fmt == "chat":
        f = output_dir / f"lean_chat_{ts}.json"
        chat = []
        for p in pairs:
            # Пропускаем negative examples (пустой tactic)
            if not p.tactic or not p.tactic.strip():
                continue
            thm_stmt = getattr(p, 'theorem_statement', '')
            if thm_stmt:
                user_content = f"I want to prove: {thm_stmt}\n\nCurrent proof state:\n```\n{p.state}\n```\n\nWhat tactic should I apply?"
            else:
                user_content = f"Prove this goal:\n```\n{p.state}\n```"
            chat.append({
                "messages": [
                    {"role": "system", "content": "You are an expert Lean 4 theorem prover. Given a theorem and proof state, suggest the next tactic."},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": p.tactic},
                ]
            })
        with open(f, "w") as fh:
            json.dump(chat, fh, indent=2, ensure_ascii=False)

    # Метаданные
    mf = output_dir / f"metadata_{ts}.json"
    with open(mf, "w") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False, default=str)

    print(f"  Датасет:    {f}  ({f.stat().st_size:,} bytes)")
    print(f"  Метаданные: {mf}")
    return f


def main():
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # elan в PATH
    os.environ["PATH"] = str(Path.home() / ".elan" / "bin") + ":" + os.environ.get("PATH", "")

    # Проверка зависимостей
    if not check_dependencies():
        print("Установите недостающие зависимости и перезапустите.")
        sys.exit(1)

    # Пути
    CACHE_BASE = Path.home() / ".cache" / "re_rl"
    REPO_DIR = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "mathlib4"
    NAV_DATA = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "navigator_data"
    OUTPUT_DIR = Path(args.output_dir) if args.output_dir else Path("datasets/formal_math_data")

    print(f"КОНФИГУРАЦИЯ")
    print(f"{'=' * 60}")
    print(f"  Mathlib:          {args.mathlib_version}")
    print(f"  Кэш:             {CACHE_BASE / f'mathlib4-{args.mathlib_version}'}")
    print(f"  Теорем:           {args.max_theorems if args.max_theorems > 0 else 'все'}")
    print(f"  Max steps/thm:    {args.max_steps}")
    print(f"  Max time/thm:     {args.max_time}с")
    print(f"  RAG model:        {args.rag_model}")
    print(f"  Output:           {OUTPUT_DIR}")
    print(f"  Format:           {args.output_format}")
    print()

    # Проверка трейсинга
    if not (REPO_DIR.parent / ".step_5_done").exists():
        print(f"ОШИБКА: Трейсинг не выполнен для {args.mathlib_version}")
        print(f"  Запустите: python scripts/fast_trace.py --version {args.mathlib_version}")
        sys.exit(1)

    build_ir = REPO_DIR / ".lake" / "build" / "ir"
    n_ast = sum(1 for _ in build_ir.rglob("*.ast.json")) if build_ir.exists() else 0
    print(f"Трейсинг: OK ({n_ast} ast.json файлов)")
    print()

    # Импортируем после проверки зависимостей
    from re_rl.tasks.formal.lean_navigator import (
        TacticTemplateExtractor,
        TacticRAG,
        PantographDojo,
        LeanNavigatorExplorer,
        load_theorems_from_env,
        TracedTheorem,
        TrainedTacticRAG,
    )

    # ═══════════════════════════════════════════════════════════
    # Шаг 1: Загрузка шаблонов тактик
    # ═══════════════════════════════════════════════════════════
    print("=" * 60)
    print("ШАГ 1: Шаблоны тактик")
    print("=" * 60)

    templates_path = NAV_DATA / "tactic_templates.json"
    NAV_DATA.mkdir(parents=True, exist_ok=True)

    extractor = TacticTemplateExtractor()

    if templates_path.exists():
        extractor.load(str(templates_path))
    else:
        print("Извлекаем шаблоны из ast.json...")
        t0 = time.time()
        extractor.extract_from_ast_dir(str(REPO_DIR))
        print(f"Время: {time.time() - t0:.1f}с")
        extractor.save(str(templates_path))

    print(f"\nТоп-10 шаблонов:")
    for tmpl, freq in extractor.get_top_templates(10):
        print(f"  [{freq:6d}] {tmpl[:65]}")
    print()

    # ═══════════════════════════════════════════════════════════
    # Шаг 2: FAISS RAG index
    # ═══════════════════════════════════════════════════════════
    print("=" * 60)
    print("ШАГ 2: FAISS RAG index")
    print("=" * 60)

    # Определяем тип RAG модели
    use_trained_rag = False
    trained_model_path = None

    if args.rag_model == "trained":
        # Ищем обученную модель в стандартном месте
        default_trained = NAV_DATA / "trained_rag" / "bert_rag_model"
        if default_trained.exists():
            trained_model_path = str(default_trained)
            use_trained_rag = True
            print(f"  Обученная BERT модель: {trained_model_path}")
        else:
            print(f"  Обученная модель не найдена: {default_trained}")
            print(f"  Запустите: python examples/train_rag.py")
            print(f"  Используем pretrained sentence-transformers...")
    elif args.rag_model != "sbert":
        # Пользователь указал путь к модели
        if Path(args.rag_model).exists():
            trained_model_path = args.rag_model
            use_trained_rag = True
            print(f"  Обученная BERT модель: {trained_model_path}")
        else:
            print(f"  Модель не найдена: {args.rag_model}")
            print(f"  Используем pretrained sentence-transformers...")

    if use_trained_rag:
        # Используем обученный BERT + FAISS L2
        trained_rag_index = NAV_DATA / "trained_rag" / "trained_rag_index"
        rag = TrainedTacticRAG(model_path=trained_model_path)

        if (trained_rag_index / "faiss_l2.index").exists():
            rag.load(str(trained_rag_index))
        else:
            print("Строим FAISS L2 index из обученного BERT...")
            t0 = time.time()
            rag.build_index(extractor.templates, min_freq=args.min_template_freq)
            print(f"Время: {time.time() - t0:.1f}с")
            rag.save(str(trained_rag_index))
    else:
        # Используем pretrained sentence-transformers (по умолчанию)
        rag_path = NAV_DATA / "rag_index"
        rag = TacticRAG(model_name="all-MiniLM-L6-v2")

        if (rag_path / "faiss.index").exists():
            rag.load(str(rag_path))
        else:
            print("Строим FAISS index...")
            t0 = time.time()
            rag.build_index(extractor.templates, min_freq=args.min_template_freq)
            print(f"Время: {time.time() - t0:.1f}с")
            rag.save(str(rag_path))
    print()

    # ═══════════════════════════════════════════════════════════
    # Шаг 3: BFS exploration через Pantograph
    # ═══════════════════════════════════════════════════════════
    print("=" * 60)
    print("ШАГ 3: BFS exploration через Pantograph")
    print("=" * 60)

    all_pairs = []
    theorem_results = []
    total_start = time.time()

    with PantographDojo(project_path=str(REPO_DIR), imports=["Mathlib"],
                        pp_full=not args.no_pp_full) as dojo:
        if args.bench:
            # Загрузка бенчмарка из JSON
            bench_path = Path(args.bench)
            if not bench_path.exists():
                print(f"ОШИБКА: бенчмарк не найден: {bench_path}")
                sys.exit(1)
            with open(bench_path) as f:
                bench_data = json.load(f)
            theorems = [
                TracedTheorem(
                    name=d["name"],
                    module=d.get("module", ""),
                    goal_state=d.get("goal_state", f"⊢ {d.get('type_pp', '')}"),
                    goal_expr=d.get("type_pp", d.get("goal_expr", "")),
                    file_path="",
                    tactics=[],
                )
                for d in bench_data
            ]
            # Применяем --max-theorems и к бенчмарку
            if args.max_theorems > 0 and len(theorems) > args.max_theorems:
                theorems = theorems[:args.max_theorems]
            print(f"Бенчмарк загружен: {len(theorems)} теорем из {bench_path}")
        else:
            # Загружаем теоремы из Lean окружения (правильные имена + полные типы)
            theorems = load_theorems_from_env(
                dojo,
                module_prefix="Mathlib",
                max_theorems=args.max_theorems if args.max_theorems > 0 else 500,
                cache_dir=str(NAV_DATA),
                verbose=args.verbose,
                validate_goals=True,
            )

        mode = "shared server" if args.no_per_file else "shared + per-file fallback"
        print(f"\nЗапускаем BFS на {len(theorems)} теоремах...")
        print(f"  max_steps={args.max_steps}, max_time={args.max_time}с")
        print(f"  goal_start mode: {mode}")
        print()

        # Парсим забаненные тактики
        banned = set()
        if args.ban_tactics:
            banned = {t.strip() for t in args.ban_tactics.split(",") if t.strip()}
        if args.no_auto:
            _NO_AUTO_SET = {
                "simp", "simp_all", "aesop", "omega", "tauto", "decide",
                "norm_num", "linarith", "ring", "trivial", "simpa",
                "positivity", "field_simp", "norm_cast", "push_cast",
                "simp_arith", "ring_nf", "nlinarith",
            }
            banned |= _NO_AUTO_SET
        if banned:
            print(f"  Забаненные тактики ({len(banned)}): {sorted(banned)}")
        if args.min_proof_length > 0:
            print(f"  Мин длина доказательства: {args.min_proof_length}")
        if args.no_pp_full:
            print(f"  Полный pretty-print: OFF (возможна обрезка ⋯)")
        if args.decompose_auto:
            print(f"  Декомпозиция automation: ВКЛ (simp→rw шаги)")

        explorer = LeanNavigatorExplorer(
            dojo=dojo, rag=rag,
            max_steps=args.max_steps,
            max_time=args.max_time,
            verbose=args.verbose,
            early_stop=not args.no_early_stop,
            banned_tactics=banned,
            decompose_auto=args.decompose_auto,
        )

        for i, thm in enumerate(theorems):
            t0 = time.time()
            try:
                result = explorer.explore(
                    goal_expr=thm.goal_expr,
                    theorem_name=thm.name,
                    theorem_code=thm.goal_state,
                    theorem_module="" if args.no_per_file else thm.module,
                    exit_on_finish=False,
                )

                # Фильтрация по min_proof_length
                if args.min_proof_length > 0:
                    filtered = [
                        p for p in result.pairs
                        if p.distance_to_proof >= args.min_proof_length
                        or p.distance_to_proof < 0  # negative examples сохраняем
                    ]
                    all_pairs.extend(filtered)
                else:
                    all_pairs.extend(result.pairs)
                elapsed = time.time() - t0

                # Статус: ✓ verified, ⚠ proven but verify failed, ○ not proven
                if result.verified:
                    status = "✓ VERIFIED"
                elif result.theorem_proven:
                    status = "⚠ UNVERIFIED"
                else:
                    status = "  ------  "

                theorem_results.append({
                    "theorem": thm.name,
                    "proven": result.theorem_proven,
                    "verified": result.verified,
                    "states": result.n_states,
                    "steps": result.n_steps,
                    "pairs": len(result.pairs),
                    "proofs_found": result.n_proofs_found,
                    "proofs_verified": result.n_proofs_verified,
                    "proof_length": len(result.proof_tactics) if result.proof_tactics else 0,
                    "n_decomposed": result.n_decomposed,
                    "time": elapsed,
                })

                if (i + 1) % 10 == 0 or result.theorem_proven:
                    proven_so_far = sum(1 for r in theorem_results if r["proven"])
                    verified_so_far = sum(1 for r in theorem_results if r.get("verified"))
                    total_pairs = sum(r["pairs"] for r in theorem_results)
                    print(f"  [{i + 1:4d}/{len(theorems)}] {status} | "
                          f"proven={proven_so_far} verified={verified_so_far} pairs={total_pairs} | "
                          f"{thm.name[:40]} ({elapsed:.1f}s)")

            except Exception as e:
                elapsed = time.time() - t0
                theorem_results.append({
                    "theorem": thm.name, "proven": False,
                    "error": str(e)[:80], "pairs": 0,
                    "states": 0, "steps": 0, "time": elapsed,
                })
                if args.verbose:
                    print(f"  [{i + 1:4d}/{len(theorems)}] ERROR | {thm.name[:45]} | {str(e)[:60]}")

    total_time = time.time() - total_start
    proofs_found = sum(1 for r in theorem_results if r.get("proven"))
    proofs_verified = sum(1 for r in theorem_results if r.get("verified"))
    false_positives = sum(1 for r in theorem_results
                         if r.get("proven") and not r.get("verified"))

    # ═══════════════════════════════════════════════════════════
    # Итоги
    # ═══════════════════════════════════════════════════════════
    print(f"\n{'=' * 60}")
    print(f"  ИТОГО")
    print(f"{'=' * 60}")
    print(f"  Теорем исследовано:     {len(theorem_results)}")
    print(f"  Доказательств найдено:  {proofs_found}")
    print(f"  Доказательств ВЕРИФИЦИРОВАНО: {proofs_verified}")
    if false_positives > 0:
        print(f"  ⚠ FALSE POSITIVE (не прошли replay): {false_positives}")
    print(f"  Training pairs:         {len(all_pairs)}")
    unique_tactics = len(set(p.tactic for p in all_pairs)) if all_pairs else 0
    print(f"  Уникальных тактик:      {unique_tactics}")
    total_decomposed = sum(r.get("n_decomposed", 0) for r in theorem_results)
    if total_decomposed > 0:
        print(f"  Декомпозировано тактик: {total_decomposed} (simp→rw шаги)")
    print(f"  Время:                  {total_time:.1f}с ({total_time / 60:.1f} мин)")

    if all_pairs:
        # Подробная статистика
        print(f"\n{'=' * 60}")
        print(f"  СТАТИСТИКА TRAINING PAIRS")
        print(f"{'=' * 60}")

        # Распределение по distance_to_proof
        dist_counts = defaultdict(int)
        for p in all_pairs:
            dist_counts[p.distance_to_proof] += 1
        print(f"\n  Распределение по distance_to_proof:")
        for d in sorted(dist_counts.keys())[:10]:
            print(f"    distance={d}: {dist_counts[d]} pairs")

        # Топ тактики
        tactic_counts = defaultdict(int)
        for p in all_pairs:
            base_tac = p.tactic.split(' ')[0] if ' ' in p.tactic else p.tactic
            tactic_counts[base_tac] += 1

        print(f"\n  Топ-15 тактик:")
        for tactic, count in sorted(tactic_counts.items(), key=lambda x: -x[1])[:15]:
            pct = 100 * count / len(all_pairs)
            print(f"    {tactic:25s} {count:5d} ({pct:.1f}%)")

        # Доказанные теоремы
        proven = [r for r in theorem_results if r.get("proven")]
        if proven:
            print(f"\n  Доказанные теоремы ({len(proven)}):")
            for r in proven[:30]:
                print(f"    {r['theorem'][:55]:55s}  steps={r['steps']:5d}  pairs={r['pairs']}")

    # ═══════════════════════════════════════════════════════════
    # Сохранение
    # ═══════════════════════════════════════════════════════════
    if all_pairs:
        print(f"\n{'=' * 60}")
        print(f"  СОХРАНЕНИЕ ДАТАСЕТА")
        print(f"{'=' * 60}")

        metadata = {
            "mathlib_version": args.mathlib_version,
            "repo_dir": str(REPO_DIR),
            "generation_date": datetime.now().isoformat(),
            "config": {
                "max_theorems": args.max_theorems,
                "max_steps_per_theorem": args.max_steps,
                "max_time_per_theorem": args.max_time,
                "min_template_freq": args.min_template_freq,
                "seed": args.seed,
            },
            "summary": {
                "total_theorems": len(theorem_results),
                "proofs_found": proofs_found,
                "proofs_verified": proofs_verified,
                "false_positives": false_positives,
                "total_pairs": len(all_pairs),
                "unique_tactics": unique_tactics,
                "total_time": total_time,
            },
            "theorem_results": theorem_results,
        }

        save_dataset(all_pairs, OUTPUT_DIR, args.output_format, metadata)
    else:
        print("\nНет данных для сохранения.")

    # Return code
    if proofs_verified > 0:
        print(f"\nУспешно! {proofs_verified} верифицированных доказательств, "
              f"{len(all_pairs)} training pairs.")
    elif proofs_found > 0:
        print(f"\n⚠ Найдено {proofs_found} доказательств, но ни одно не прошло replay-верификацию!")
    else:
        print(f"\nНе удалось доказать ни одной теоремы. "
              f"Попробуйте увеличить --max-steps и --max-time.")

    return 0 if proofs_verified > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
