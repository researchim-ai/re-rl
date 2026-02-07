#!/usr/bin/env python3
"""
Параллельная BFS exploration теорем Lean 4 через Ray + Pantograph.

Аналог run_bfs.py, но с Ray-параллелизацией:
  - Каждый worker создаёт свой PantographDojo + RAG
  - Теоремы распределяются по workers
  - Результаты собираются в общий датасет

Вдохновлено оригинальным кодом LeanNavigator:
  - 24 параллельных процесса, 28 дней, 4.7M теорем

Использование:
    # 4 worker'а, по 50 теорем на worker
    python examples/run_bfs_parallel.py --num-workers 4 --max-theorems 200

    # Полный прогон (всё что может машина)
    python examples/run_bfs_parallel.py --num-workers 8 --max-theorems 0 --max-time 300

    # Быстрый тест
    python examples/run_bfs_parallel.py --num-workers 2 --max-theorems 20 --max-steps 3000

Предварительно:
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
        description="Параллельная BFS exploration (Ray) → training pairs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python examples/run_bfs_parallel.py --num-workers 4 --max-theorems 200
  python examples/run_bfs_parallel.py --num-workers 8 --max-theorems 0 --max-time 300
  python examples/run_bfs_parallel.py --num-workers 2 --max-theorems 20 --verbose
        """,
    )
    parser.add_argument("--mathlib-version", default="v4.26.0",
                        help="Версия Mathlib4 (default: v4.26.0)")
    parser.add_argument("--num-workers", type=int, default=4,
                        help="Количество параллельных Ray worker'ов (default: 4)")
    parser.add_argument("--max-theorems", type=int, default=200,
                        help="Макс теорем для BFS (0 = все, default: 200)")
    parser.add_argument("--max-steps", type=int, default=5000,
                        help="Макс шагов BFS на теорему (default: 5000)")
    parser.add_argument("--max-time", type=int, default=60,
                        help="Секунд на теорему (default: 60)")
    parser.add_argument("--min-template-freq", type=int, default=3,
                        help="Мин частота шаблона для RAG (default: 3)")
    parser.add_argument("--output-dir", default=None,
                        help="Директория для результатов")
    parser.add_argument("--rag-model", default="sbert",
                        help="RAG модель: 'sbert', 'trained', или путь")
    parser.add_argument("--output-format", default="jsonl",
                        choices=["jsonl", "json", "sft", "chat"],
                        help="Формат датасета (default: jsonl)")
    parser.add_argument("--verbose", action="store_true",
                        help="Подробный вывод")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed")
    parser.add_argument("--no-per-file", action="store_true",
                        help="Не использовать per-file server fallback")
    parser.add_argument("--no-early-stop", action="store_true",
                        help="Отключить раннюю остановку (1/3 бюджета)")
    parser.add_argument("--num-cpus", type=int, default=None,
                        help="Всего CPU для Ray (default: auto)")
    parser.add_argument("--memory-gb", type=int, default=None,
                        help="RAM для Ray в GB (default: auto)")
    return parser.parse_args()


# ═══════════════════════════════════════════════════════════════
# Ray worker: обрабатывает batch теорем
# ═══════════════════════════════════════════════════════════════

def _bfs_worker(
    worker_id: int,
    theorem_dicts: list,
    repo_dir: str,
    nav_data_dir: str,
    rag_model: str,
    min_template_freq: int,
    max_steps: int,
    max_time: int,
    use_per_file: bool,
    early_stop: bool,
    verbose: bool,
):
    """
    Ray worker: создаёт PantographDojo + RAG, обрабатывает batch теорем.

    Каждый worker — изолированный процесс со своим Lean server.
    Это гарантирует отсутствие конфликтов между workers.
    """
    import asyncio
    import os
    import time

    # Ray использует uvloop, но pantograph/nest_asyncio не совместимы с ним.
    # Сбрасываем event loop policy на стандартный asyncio ДО импорта pantograph.
    asyncio.set_event_loop_policy(None)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    # elan в PATH (в каждом worker процессе)
    os.environ["PATH"] = str(Path.home() / ".elan" / "bin") + ":" + os.environ.get("PATH", "")

    from re_rl.tasks.formal.lean_navigator import (
        TacticTemplateExtractor,
        TacticRAG,
        PantographDojo,
        LeanNavigatorExplorer,
        TracedTheorem,
        TrainedTacticRAG,
    )

    nav_data = Path(nav_data_dir)
    n_thms = len(theorem_dicts)
    print(f"[Worker {worker_id}] Запуск: {n_thms} теорем")

    # ── 1. Загрузка шаблонов тактик (из кэша) ──
    templates_path = nav_data / "tactic_templates.json"
    extractor = TacticTemplateExtractor()
    extractor.load(str(templates_path))

    # ── 2. Загрузка/построение RAG ──
    use_trained_rag = False
    trained_model_path = None

    if rag_model == "trained":
        default_trained = nav_data / "trained_rag" / "bert_rag_model"
        if default_trained.exists():
            trained_model_path = str(default_trained)
            use_trained_rag = True
    elif rag_model != "sbert":
        if Path(rag_model).exists():
            trained_model_path = rag_model
            use_trained_rag = True

    if use_trained_rag:
        trained_rag_index = nav_data / "trained_rag" / "trained_rag_index"
        rag = TrainedTacticRAG(model_path=trained_model_path)
        if (trained_rag_index / "faiss_l2.index").exists():
            rag.load(str(trained_rag_index))
        else:
            rag.build_index(extractor.templates, min_freq=min_template_freq)
    else:
        rag_path = nav_data / "rag_index"
        rag = TacticRAG(model_name="all-MiniLM-L6-v2")
        if (rag_path / "faiss.index").exists():
            rag.load(str(rag_path))
        else:
            rag.build_index(extractor.templates, min_freq=min_template_freq)

    print(f"[Worker {worker_id}] RAG загружен")

    # ── 3. Восстанавливаем TracedTheorem из dict ──
    theorems = [
        TracedTheorem(
            name=d["name"],
            module=d["module"],
            goal_state=d["goal_state"],
            goal_expr=d["goal_expr"],
            file_path=d.get("file_path", ""),
            tactics=d.get("tactics", []),
        )
        for d in theorem_dicts
    ]

    # ── 4. BFS exploration ──
    worker_pairs = []
    worker_results = []

    with PantographDojo(project_path=repo_dir, imports=["Mathlib"]) as dojo:
        explorer = LeanNavigatorExplorer(
            dojo=dojo, rag=rag,
            max_steps=max_steps, max_time=max_time,
            verbose=verbose,
            early_stop=early_stop,
        )

        for i, thm in enumerate(theorems):
            t0 = time.time()
            try:
                result = explorer.explore(
                    goal_expr=thm.goal_expr,
                    theorem_name=thm.name,
                    theorem_code=thm.goal_state,
                    theorem_module="" if not use_per_file else thm.module,
                    exit_on_finish=False,
                )

                # Конвертируем pairs в dict (для сериализации через Ray)
                pairs_dicts = [
                    {
                        "state": p.state,
                        "tactic": p.tactic,
                        "next_state": p.next_state,
                        "distance_to_proof": p.distance_to_proof,
                        "theorem_name": p.theorem_name,
                    }
                    for p in result.pairs
                ]
                worker_pairs.extend(pairs_dicts)

                elapsed = time.time() - t0
                status = "✓" if result.verified else ("⚠" if result.theorem_proven else "○")

                worker_results.append({
                    "theorem": thm.name,
                    "proven": result.theorem_proven,
                    "verified": result.verified,
                    "states": result.n_states,
                    "steps": result.n_steps,
                    "pairs": len(result.pairs),
                    "proofs_found": result.n_proofs_found,
                    "proofs_verified": result.n_proofs_verified,
                    "proof_length": len(result.proof_tactics) if result.proof_tactics else 0,
                    "time": elapsed,
                })

                if result.theorem_proven or (i + 1) % 5 == 0:
                    proven = sum(1 for r in worker_results if r["proven"])
                    verified = sum(1 for r in worker_results if r.get("verified"))
                    total_p = sum(r["pairs"] for r in worker_results)
                    print(f"  [W{worker_id} {i+1}/{n_thms}] {status} "
                          f"proven={proven} verified={verified} pairs={total_p} | "
                          f"{thm.name[:35]} ({elapsed:.1f}s)")

            except Exception as e:
                elapsed = time.time() - t0
                worker_results.append({
                    "theorem": thm.name, "proven": False,
                    "error": str(e)[:80], "pairs": 0,
                    "states": 0, "steps": 0, "time": elapsed,
                })
                if verbose:
                    print(f"  [W{worker_id}] ERROR: {thm.name[:35]} | {str(e)[:60]}")

    proven = sum(1 for r in worker_results if r["proven"])
    verified = sum(1 for r in worker_results if r.get("verified"))
    print(f"[Worker {worker_id}] Готово: {proven} proven, {verified} verified, "
          f"{len(worker_pairs)} pairs из {n_thms} теорем")

    return {
        "worker_id": worker_id,
        "pairs": worker_pairs,
        "results": worker_results,
    }


def save_dataset(pairs_dicts, output_dir, fmt, metadata):
    """Сохраняет датасет (pairs уже как dicts)."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    if fmt == "jsonl":
        f = output_dir / f"lean_data_{ts}.jsonl"
        with open(f, "w") as fh:
            for p in pairs_dicts:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    elif fmt == "json":
        f = output_dir / f"lean_data_{ts}.json"
        with open(f, "w") as fh:
            json.dump(pairs_dicts, fh, indent=2, ensure_ascii=False)
    elif fmt == "sft":
        f = output_dir / f"lean_sft_{ts}.json"
        sft = [{
            "instruction": "You are a Lean 4 theorem prover. Given the current proof state, suggest the next tactic.",
            "input": f"Current proof state:\n{p['state']}",
            "output": p["tactic"],
        } for p in pairs_dicts]
        with open(f, "w") as fh:
            json.dump(sft, fh, indent=2, ensure_ascii=False)
    elif fmt == "chat":
        f = output_dir / f"lean_chat_{ts}.json"
        chat = [{
            "messages": [
                {"role": "system", "content": "You are an expert Lean 4 theorem prover."},
                {"role": "user", "content": f"Prove this goal:\n```\n{p['state']}\n```"},
                {"role": "assistant", "content": p["tactic"]},
            ]
        } for p in pairs_dicts]
        with open(f, "w") as fh:
            json.dump(chat, fh, indent=2, ensure_ascii=False)

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

    # Пути
    CACHE_BASE = Path.home() / ".cache" / "re_rl"
    REPO_DIR = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "mathlib4"
    NAV_DATA = CACHE_BASE / f"mathlib4-{args.mathlib_version}" / "navigator_data"
    OUTPUT_DIR = Path(args.output_dir) if args.output_dir else Path("datasets/formal_math_data")

    print(f"{'=' * 60}")
    print(f"  PARALLEL BFS EXPLORATION (Ray)")
    print(f"{'=' * 60}")
    print(f"  Workers:          {args.num_workers}")
    print(f"  Mathlib:          {args.mathlib_version}")
    print(f"  Теорем:           {args.max_theorems if args.max_theorems > 0 else 'все'}")
    print(f"  Max steps/thm:    {args.max_steps}")
    print(f"  Max time/thm:     {args.max_time}с")
    print(f"  RAG model:        {args.rag_model}")
    print(f"  Output:           {OUTPUT_DIR}")
    print()

    # Проверка трейсинга
    if not (REPO_DIR.parent / ".step_5_done").exists():
        print(f"ОШИБКА: Трейсинг не выполнен для {args.mathlib_version}")
        print(f"  Запустите: python scripts/fast_trace.py --version {args.mathlib_version}")
        sys.exit(1)

    # ═══════════════════════════════════════════════════════════
    # Шаг 1: Убеждаемся что шаблоны и RAG закэшированы
    # ═══════════════════════════════════════════════════════════
    print("Проверка кэша шаблонов и RAG...")
    templates_path = NAV_DATA / "tactic_templates.json"
    NAV_DATA.mkdir(parents=True, exist_ok=True)

    if not templates_path.exists():
        print("Шаблоны не найдены — извлекаем (один раз)...")
        from re_rl.tasks.formal.lean_navigator import TacticTemplateExtractor
        extractor = TacticTemplateExtractor()
        extractor.extract_from_ast_dir(str(REPO_DIR))
        extractor.save(str(templates_path))
    else:
        print(f"  Шаблоны: OK ({templates_path})")

    # Проверяем/строим RAG index заранее (workers загрузят из кэша)
    rag_ready = False
    if args.rag_model == "trained":
        idx = NAV_DATA / "trained_rag" / "trained_rag_index" / "faiss_l2.index"
        rag_ready = idx.exists()
        if not rag_ready:
            print("Trained RAG index не найден — строим...")
            from re_rl.tasks.formal.lean_navigator import (
                TacticTemplateExtractor, TrainedTacticRAG,
            )
            ext = TacticTemplateExtractor()
            ext.load(str(templates_path))
            model_path = str(NAV_DATA / "trained_rag" / "bert_rag_model")
            rag = TrainedTacticRAG(model_path=model_path)
            rag.build_index(ext.templates, min_freq=args.min_template_freq)
            rag.save(str(NAV_DATA / "trained_rag" / "trained_rag_index"))
            rag_ready = True
    elif args.rag_model == "sbert":
        idx = NAV_DATA / "rag_index" / "faiss.index"
        rag_ready = idx.exists()
        if not rag_ready:
            print("SBERT RAG index не найден — строим...")
            from re_rl.tasks.formal.lean_navigator import (
                TacticTemplateExtractor, TacticRAG,
            )
            ext = TacticTemplateExtractor()
            ext.load(str(templates_path))
            rag = TacticRAG(model_name="all-MiniLM-L6-v2")
            rag.build_index(ext.templates, min_freq=args.min_template_freq)
            rag.save(str(NAV_DATA / "rag_index"))
            rag_ready = True

    print(f"  RAG index: {'OK' if rag_ready else 'будет построен в worker'}")

    # ═══════════════════════════════════════════════════════════
    # Шаг 2: Загрузка теорем (в main процессе, один раз)
    # ═══════════════════════════════════════════════════════════
    print("\nЗагрузка теорем из Lean env...")

    from re_rl.tasks.formal.lean_navigator import (
        PantographDojo,
        load_theorems_from_env,
    )

    max_thms = args.max_theorems if args.max_theorems > 0 else 5000

    with PantographDojo(project_path=str(REPO_DIR), imports=["Mathlib"]) as dojo:
        theorems = load_theorems_from_env(
            dojo,
            module_prefix="Mathlib",
            max_theorems=max_thms,
            cache_dir=str(NAV_DATA),
            verbose=args.verbose,
            validate_goals=True,
        )

    print(f"Загружено {len(theorems)} теорем для {args.num_workers} workers")

    # Конвертируем в dict для сериализации через Ray
    theorem_dicts = [
        {
            "name": t.name,
            "module": t.module,
            "goal_state": t.goal_state,
            "goal_expr": t.goal_expr,
            "file_path": t.file_path,
            "tactics": t.tactics,
        }
        for t in theorems
    ]

    # ═══════════════════════════════════════════════════════════
    # Шаг 3: Распределяем теоремы по workers и запускаем Ray
    # ═══════════════════════════════════════════════════════════
    import ray

    # Разбиваем на батчи
    n_workers = min(args.num_workers, len(theorem_dicts))
    if n_workers <= 0:
        print("Нет теорем для обработки.")
        sys.exit(0)

    batch_size = len(theorem_dicts) // n_workers
    batches = []
    for i in range(n_workers):
        start = i * batch_size
        end = start + batch_size if i < n_workers - 1 else len(theorem_dicts)
        batches.append(theorem_dicts[start:end])

    print(f"\nРаспределение: {len(theorem_dicts)} теорем → {n_workers} workers "
          f"(~{batch_size} на worker)")

    # Инициализация Ray
    ray_kwargs = {}
    if args.num_cpus:
        ray_kwargs["num_cpus"] = args.num_cpus
    if args.memory_gb:
        ray_kwargs["_memory"] = args.memory_gb * 1024 * 1024 * 1024

    if ray.is_initialized():
        ray.shutdown()

    ray.init(**ray_kwargs)
    print(f"Ray инициализирован: {ray.cluster_resources()}")

    # Создаём remote функцию
    bfs_worker_remote = ray.remote(num_cpus=1)(_bfs_worker)

    # Запускаем workers
    total_start = time.time()
    print(f"\nЗапуск {n_workers} workers...")
    print("=" * 60)

    futures = []
    for i, batch in enumerate(batches):
        future = bfs_worker_remote.remote(
            worker_id=i,
            theorem_dicts=batch,
            repo_dir=str(REPO_DIR),
            nav_data_dir=str(NAV_DATA),
            rag_model=args.rag_model,
            min_template_freq=args.min_template_freq,
            max_steps=args.max_steps,
            max_time=args.max_time,
            use_per_file=not args.no_per_file,
            early_stop=not args.no_early_stop,
            verbose=args.verbose,
        )
        futures.append(future)

    # Собираем результаты по мере готовности
    all_pairs = []
    all_results = []

    remaining = list(futures)
    while remaining:
        done, remaining = ray.wait(remaining, num_returns=1, timeout=10.0)
        for ref in done:
            try:
                worker_output = ray.get(ref)
                wid = worker_output["worker_id"]
                wp = worker_output["pairs"]
                wr = worker_output["results"]
                all_pairs.extend(wp)
                all_results.extend(wr)

                proven = sum(1 for r in wr if r.get("proven"))
                verified = sum(1 for r in wr if r.get("verified"))
                print(f"\n  Worker {wid} завершён: "
                      f"{proven} proven, {verified} verified, "
                      f"{len(wp)} pairs из {len(wr)} теорем")
            except Exception as e:
                print(f"\n  Worker ОШИБКА: {e}")

    ray.shutdown()
    total_time = time.time() - total_start

    # ═══════════════════════════════════════════════════════════
    # Итоги
    # ═══════════════════════════════════════════════════════════
    proofs_found = sum(1 for r in all_results if r.get("proven"))
    proofs_verified = sum(1 for r in all_results if r.get("verified"))
    false_positives = sum(1 for r in all_results
                         if r.get("proven") and not r.get("verified"))
    unique_tactics = len(set(p["tactic"] for p in all_pairs)) if all_pairs else 0

    print(f"\n{'=' * 60}")
    print(f"  ИТОГО (параллельный запуск)")
    print(f"{'=' * 60}")
    print(f"  Workers:                {n_workers}")
    print(f"  Теорем исследовано:     {len(all_results)}")
    print(f"  Доказательств найдено:  {proofs_found}")
    print(f"  Верифицировано:         {proofs_verified}")
    if false_positives > 0:
        print(f"  ⚠ FALSE POSITIVE:       {false_positives}")
    print(f"  Training pairs:         {len(all_pairs)}")
    print(f"  Уникальных тактик:      {unique_tactics}")
    print(f"  Время:                  {total_time:.1f}с ({total_time / 60:.1f} мин)")
    print(f"  Ускорение:              ~{n_workers}x (vs sequential)")

    if all_pairs:
        # Статистика
        print(f"\n{'=' * 60}")
        print(f"  СТАТИСТИКА")
        print(f"{'=' * 60}")

        dist_counts = defaultdict(int)
        for p in all_pairs:
            dist_counts[p["distance_to_proof"]] += 1
        print(f"\n  Distance to proof:")
        for d in sorted(dist_counts.keys())[:10]:
            print(f"    distance={d}: {dist_counts[d]} pairs")

        tactic_counts = defaultdict(int)
        for p in all_pairs:
            base_tac = p["tactic"].split(' ')[0] if ' ' in p["tactic"] else p["tactic"]
            tactic_counts[base_tac] += 1
        print(f"\n  Топ-15 тактик:")
        for tac, count in sorted(tactic_counts.items(), key=lambda x: -x[1])[:15]:
            pct = 100 * count / len(all_pairs)
            print(f"    {tac:25s} {count:5d} ({pct:.1f}%)")

        proven_thms = [r for r in all_results if r.get("verified")]
        if proven_thms:
            print(f"\n  Верифицированные теоремы ({len(proven_thms)}):")
            for r in sorted(proven_thms, key=lambda x: -x["pairs"])[:30]:
                print(f"    {r['theorem'][:50]:50s}  "
                      f"steps={r['steps']:5d}  pairs={r['pairs']:4d}  "
                      f"len={r.get('proof_length', 0)}")

        # Сохранение
        print(f"\n{'=' * 60}")
        print(f"  СОХРАНЕНИЕ")
        print(f"{'=' * 60}")

        metadata = {
            "mathlib_version": args.mathlib_version,
            "repo_dir": str(REPO_DIR),
            "generation_date": datetime.now().isoformat(),
            "parallel": True,
            "num_workers": n_workers,
            "config": {
                "max_theorems": args.max_theorems,
                "max_steps_per_theorem": args.max_steps,
                "max_time_per_theorem": args.max_time,
                "min_template_freq": args.min_template_freq,
                "rag_model": args.rag_model,
                "seed": args.seed,
            },
            "summary": {
                "total_theorems": len(all_results),
                "proofs_found": proofs_found,
                "proofs_verified": proofs_verified,
                "false_positives": false_positives,
                "total_pairs": len(all_pairs),
                "unique_tactics": unique_tactics,
                "total_time": total_time,
            },
            "theorem_results": all_results,
        }

        save_dataset(all_pairs, OUTPUT_DIR, args.output_format, metadata)
    else:
        print("\nНет данных для сохранения.")

    if proofs_verified > 0:
        print(f"\nУспешно! {proofs_verified} верифицированных доказательств, "
              f"{len(all_pairs)} training pairs за {total_time:.0f}с.")
    else:
        print(f"\nНе удалось доказать ни одной теоремы.")

    return 0 if proofs_verified > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
