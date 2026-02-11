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
from typing import Optional


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
    parser.add_argument("--ban-tactics", default=None,
                        help="Забаненные тактики через запятую")
    parser.add_argument("--no-auto", action="store_true",
                        help="Пресет: забанить нуклеарные тактики-упрощатели")
    parser.add_argument("--min-proof-length", type=int, default=0,
                        help="Мин distance_to_proof для пар")
    parser.add_argument("--decompose-auto", action="store_true",
                        help="Декомпозиция simp/aesop в rw-шаги. "
                             "Расширяет датасет содержательными леммами.")
    parser.add_argument("--no-pp-full", action="store_true",
                        help="Отключить полный pretty-print (разрешить ⋯ обрезку). "
                             "По умолчанию pp_full=True — полный вывод без обрезки.")
    parser.add_argument("--max-pairs-per-worker", type=int, default=40000,
                        help="Макс пар на worker (default: 40000)")
    parser.add_argument("--max-states-per-theorem", type=int, default=2500,
                        help="Макс состояний BFS на теорему (default: 2500)")
    parser.add_argument("--debug-mem", action="store_true",
                        help="Логировать разбивку памяти (self + дочерние) после каждой теоремы в worker")
    parser.add_argument("--debug-tracemalloc", action="store_true",
                        help="В worker: tracemalloc — топ аллокаций после каждой теоремы")
    parser.add_argument("--gc-interval", type=int, default=1,
                        help="Вызывать gc() каждые N теорем (0=никогда, default=1)")
    parser.add_argument("--restart-interval", type=int, default=0,
                        help="Перезапускать Lean dojo каждые N теорем для очистки памяти (0=никогда, default=0)")
    parser.add_argument("--min-free-gb", type=float, default=12.0,
                        help="Не начинать новую теорему, если свободной памяти меньше N GB (default: 12, 0=отключить)")
    parser.add_argument("--max-worker-rss-mb", type=int, default=7500,
                        help="Макс RSS (Python+Lean) на воркер в MB; при превышении BFS досрочно завершает теорему (default: 7500, 0=отключить)")
    parser.add_argument("--max-tactic-rss-jump-mb", type=int, default=0,
                        help="Если >0, досрочно завершать теорему при скачке RSS на одной тактике больше N MB")
    parser.add_argument("--diag-jsonl", action="store_true",
                        help="Писать JSONL-диагностику (theorem_start/progress/error/phase) по воркерам")
    parser.add_argument("--trace-theorem", default="",
                        help="Подстрока имени теоремы для детальной трассировки run_tac")
    parser.add_argument("--trace-every-tac", action="store_true",
                        help="Логировать before/after run_tac (рекомендуется только с --trace-theorem)")
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
    banned_tactics: Optional[set] = None,
    decompose_auto: bool = False,
    min_proof_length: int = 0,
    pp_full: bool = False,
    max_pairs_per_worker: int = 40000,
    max_states_per_theorem: int = 2500,
    debug_mem: bool = False,
    debug_tracemalloc: bool = False,
    gc_interval: int = 1,
    restart_interval: int = 25,
    min_free_gb: float = 12.0,
    max_worker_rss_mb: int = 7500,
    max_tactic_rss_jump_mb: int = 0,
    diag_jsonl: bool = False,
    trace_theorem: str = "",
    trace_every_tac: bool = False,
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

    _tracemalloc_prev_snap = None
    if debug_tracemalloc:
        import tracemalloc
        tracemalloc.start(10)
        print(f"[Worker {worker_id}] tracemalloc включён (дифф после каждой теоремы)", flush=True)

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

    # ── Логирование в файл (для диагностики OOM) ──
    log_dir = Path(nav_data_dir).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"worker_{worker_id}.log"
    diag_file = log_dir / f"worker_{worker_id}.jsonl"
    
    def _log_to_file(msg: str):
        """Пишет в файл с flush (не потеряется при OOM)."""
        try:
            import datetime
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"[{ts}] {msg}\n")
                f.flush()
        except:
            pass

    def _diag(event: str, **payload):
        """Структурированный JSONL лог для post-mortem анализа OOM."""
        if not diag_jsonl:
            return
        try:
            rec = {
                "ts": time.time(),
                "worker_id": worker_id,
                "event": event,
                **payload,
            }
            with open(diag_file, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
        except Exception:
            pass

    def _get_full_mem_info() -> str:
        """Полная информация о памяти."""
        try:
            import psutil
            proc = psutil.Process()
            py_mb = proc.memory_info().rss / (1024 * 1024)
            
            # Дочерние процессы (Lean) этого worker
            children_info = []
            lean_total = 0
            for c in proc.children(recursive=True):
                try:
                    c_mb = c.memory_info().rss / (1024 * 1024)
                    lean_total += c_mb
                    cmd = c.name()[:20] if c.name() else "?"
                    children_info.append(f"{cmd}={c_mb:.0f}MB")
                except:
                    pass
            
            # ВСЕ pantograph процессы в системе (чтобы видеть реальную картину)
            all_panto = []
            all_panto_mb = 0
            for p in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'pantograph' in (p.info['name'] or '').lower():
                        mb = p.info['memory_info'].rss / (1024 * 1024)
                        all_panto.append(f"{mb:.0f}")
                        all_panto_mb += mb
                except:
                    pass
            
            # Системная память
            vm = psutil.virtual_memory()
            sys_used = vm.used / (1024**3)
            sys_total = vm.total / (1024**3)
            sys_avail = vm.available / (1024**3)
            
            panto_str = f" | ALL_PANTO: {len(all_panto)} procs, {all_panto_mb/1024:.1f}GB" if all_panto else ""
            return (f"Python={py_mb:.0f}MB | Lean={lean_total:.0f}MB [{', '.join(children_info[:3])}] | "
                    f"System: {sys_used:.1f}/{sys_total:.1f}GB used, {sys_avail:.1f}GB free{panto_str}")
        except Exception as e:
            return f"mem_error: {e}"

    _log_to_file(f"=== Worker {worker_id} START === {n_thms} теорем")
    _log_to_file(f"MEM: {_get_full_mem_info()}")
    _diag("worker_start", n_theorems=n_thms, mem=_get_full_mem_info())

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

    def _log_memory_breakdown(worker_id: int, stage: str):
        """Пишет в stderr разбивку: RSS текущего процесса + каждый дочерний (pid, cmdline, rss)."""
        try:
            import psutil
            me = psutil.Process()
            self_mb = me.memory_info().rss / (1024 * 1024)
            parts = [f"self={self_mb:.0f}MB"]
            total = self_mb
            for c in me.children(recursive=True):
                try:
                    rss_mb = c.memory_info().rss / (1024 * 1024)
                    total += rss_mb
                    cmd = (c.name() or "?") if hasattr(c, "name") else "?"
                    if c.cmdline():
                        cmd = " ".join(c.cmdline())[:60].replace("\n", " ")
                    parts.append(f"pid{c.pid}({cmd})={rss_mb:.0f}MB")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            print(f"  [W{worker_id} MEM] {stage} | {' | '.join(parts)} | total={total:.0f}MB", flush=True)
        except Exception as e:
            print(f"  [W{worker_id} MEM] {stage} | error: {e}", flush=True)

    if debug_mem:
        _log_memory_breakdown(worker_id, "after_rag_before_dojo")

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

    # Настройки управления памятью (из аргументов)
    GC_INTERVAL = gc_interval
    RESTART_INTERVAL = restart_interval
    MIN_FREE_GB = min_free_gb
    MAX_WORKER_RSS_MB = max_worker_rss_mb
    MAX_TACTIC_RSS_JUMP_MB = max_tactic_rss_jump_mb
    TRACE_THEOREM = trace_theorem
    TRACE_EVERY_TAC = trace_every_tac
    current_theorem_name = ""

    def _create_dojo():
        d = PantographDojo(project_path=repo_dir, imports=["Mathlib"], pp_full=pp_full)
        d.start()
        return d

    def _create_explorer(dojo_instance):
        def _on_bfs_progress(step: int, states: int, rss_mb: float) -> None:
            _log_to_file(f"    BFS progress: step={step} states={states} rss_mb={rss_mb:.0f}")
            _diag(
                "bfs_progress",
                theorem=current_theorem_name,
                step=step,
                states=states,
                rss_mb=round(rss_mb, 2),
            )

        def _on_phase(event: str, data: dict) -> None:
            _diag(event, theorem=current_theorem_name, **data)

        return LeanNavigatorExplorer(
            dojo=dojo_instance, rag=rag,
            max_steps=max_steps, max_time=max_time,
            verbose=verbose,
            early_stop=early_stop,
            banned_tactics=banned_tactics,
            decompose_auto=decompose_auto,
            max_states=max_states_per_theorem,
            max_process_rss_mb=MAX_WORKER_RSS_MB,
            max_tactic_rss_jump_mb=MAX_TACTIC_RSS_JUMP_MB,
            progress_callback=_on_bfs_progress,
            trace_tactics=TRACE_EVERY_TAC,
            trace_theorem_substr=TRACE_THEOREM,
            phase_callback=_on_phase,
        )

    dojo = _create_dojo()
    explorer = _create_explorer(dojo)

    if debug_mem:
        _log_memory_breakdown(worker_id, "after_dojo_start_before_theorems")
    if debug_tracemalloc:
        import tracemalloc
        _tracemalloc_prev_snap = tracemalloc.take_snapshot()
        print(f"[Worker {worker_id}] tracemalloc: базовый снимок (до теорем)", flush=True)

    consecutive_errors = 0
    MAX_CONSECUTIVE_ERRORS = 5  # Если много подряд — dojo сломан (Lean PANIC)

    _log_to_file(f"Dojo started. MEM: {_get_full_mem_info()}")

    try:
        for i, thm in enumerate(theorems):
            t0 = time.time()
            current_theorem_name = thm.name
            
            # ===== ЛОГИРУЕМ ДО НАЧАЛА ТЕОРЕМЫ (для диагностики OOM) =====
            _log_to_file(f">>> STARTING theorem {i+1}/{n_thms}: {thm.name}")
            _log_to_file(f"    goal_expr length: {len(thm.goal_expr)} chars")
            _log_to_file(f"    MEM BEFORE: {_get_full_mem_info()}")
            _diag(
                "theorem_start",
                theorem=thm.name,
                theorem_idx=i + 1,
                n_theorems=n_thms,
                goal_expr_len=len(thm.goal_expr),
                mem=_get_full_mem_info(),
            )
            
            # Проверка свободной памяти: не начинаем теорему, если мало RAM (избегаем OOM)
            if MIN_FREE_GB > 0:
                try:
                    vm = psutil.virtual_memory()
                    free_gb = vm.available / (1024**3)
                    if free_gb < MIN_FREE_GB:
                        _log_to_file(f"    SKIP (low memory: {free_gb:.1f}GB free < {MIN_FREE_GB}GB)")
                        _diag("theorem_skip_low_memory", theorem=thm.name, free_gb=round(free_gb, 3), min_free_gb=MIN_FREE_GB)
                        print(f"  [W{worker_id}] SKIP {thm.name[:40]} (free {free_gb:.1f}GB < {MIN_FREE_GB}GB)")
                        worker_results.append({
                            "theorem": thm.name, "proven": False, "verified": False,
                            "states": 0, "steps": 0, "pairs": 0,
                            "proofs_found": 0, "proofs_verified": 0, "proof_length": 0,
                            "n_decomposed": 0, "time": 0,
                            "error": f"skipped: low memory ({free_gb:.1f}GB free)",
                        })
                        gc.collect()
                        if GC_INTERVAL > 0:
                            try:
                                dojo.server.gc()
                            except Exception:
                                pass
                        continue
                except Exception:
                    pass
            
            try:
                result = explorer.explore(
                    goal_expr=thm.goal_expr,
                    theorem_name=thm.name,
                    theorem_code=thm.goal_state,
                    theorem_module="" if not use_per_file else thm.module,
                    exit_on_finish=False,
                )

                # ===== ЛОГИРУЕМ СРАЗУ ПОСЛЕ explore() =====
                _log_to_file(f"    DONE explore: states={result.n_states}, steps={result.n_steps}, "
                            f"pairs={len(result.pairs)}, proven={result.theorem_proven}")
                _log_to_file(f"    MEM AFTER explore: {_get_full_mem_info()}")
                _diag(
                    "theorem_done",
                    theorem=thm.name,
                    states=result.n_states,
                    steps=result.n_steps,
                    pairs=len(result.pairs),
                    proven=bool(result.theorem_proven),
                    verified=bool(result.verified),
                    mem=_get_full_mem_info(),
                )

                # Фильтрация по min_proof_length + конвертация в dict
                filtered_pairs = result.pairs
                if min_proof_length > 0:
                    filtered_pairs = [
                        p for p in result.pairs
                        if p.distance_to_proof >= min_proof_length
                        or p.distance_to_proof < 0  # negative examples сохраняем
                    ]
                # Ограничиваем длину строк (снижает память и риск OOM)
                _MAX_STATE_LEN = 12000
                def _trunc(s: str) -> str:
                    return (s[: _MAX_STATE_LEN] + "\n...[truncated]") if len(s) > _MAX_STATE_LEN else s
                pairs_dicts = [
                    {
                        "state": _trunc(p.state),
                        "tactic": p.tactic,
                        "next_state": _trunc(p.next_state),
                        "distance_to_proof": p.distance_to_proof,
                        "theorem_name": p.theorem_name,
                        "theorem_statement": _trunc(getattr(p, 'theorem_statement', '')),
                    }
                    for p in filtered_pairs
                ]
                worker_pairs.extend(pairs_dicts)
                if len(worker_pairs) >= max_pairs_per_worker:
                    print(f"  [W{worker_id}] Достигнут лимит {max_pairs_per_worker} пар — завершаем worker")
                    break

                elapsed = time.time() - t0
                status = "✓" if result.verified else ("⚠" if result.theorem_proven else "○")

                worker_results.append({
                    "theorem": thm.name,
                    "proven": result.theorem_proven,
                    "verified": result.verified,
                    "states": result.n_states,
                    "steps": result.n_steps,
                    "pairs": len(filtered_pairs),
                    "proofs_found": result.n_proofs_found,
                    "proofs_verified": result.n_proofs_verified,
                    "proof_length": len(result.proof_tactics) if result.proof_tactics else 0,
                    "n_decomposed": result.n_decomposed,
                    "time": elapsed,
                })

                # Память после каждой теоремы (ВСЕГДА логируем для диагностики OOM)
                mem_warning = ""
                try:
                    import psutil
                    proc = psutil.Process()
                    py_mb = proc.memory_info().rss / (1024 * 1024)
                    lean_mb = sum(c.memory_info().rss for c in proc.children(recursive=True)) / (1024 * 1024)
                    vm = psutil.virtual_memory()
                    sys_used_gb = vm.used / (1024**3)
                    sys_total_gb = vm.total / (1024**3)
                    sys_avail_gb = vm.available / (1024**3)
                    mem_info = f"Py={py_mb:.0f}MB Lean={lean_mb:.0f}MB Sys={sys_used_gb:.1f}/{sys_total_gb:.1f}GB"
                    # Предупреждение если мало свободной памяти
                    if sys_avail_gb < 4:
                        mem_warning = f" ⚠⚠⚠ КРИТИЧНО: осталось {sys_avail_gb:.1f}GB!"
                    elif sys_avail_gb < 8:
                        mem_warning = f" ⚠ мало памяти: {sys_avail_gb:.1f}GB свободно"
                except:
                    mem_info = ""

                # Выводим КАЖДУЮ теорему если мало памяти или есть предупреждение
                force_print = bool(mem_warning) or result.n_states > 500

                if result.theorem_proven or (i + 1) % 5 == 0 or force_print:
                    proven = sum(1 for r in worker_results if r["proven"])
                    verified = sum(1 for r in worker_results if r.get("verified"))
                    total_p = sum(r["pairs"] for r in worker_results)
                    print(f"  [W{worker_id} {i+1}/{n_thms}] {status} "
                          f"proven={proven} verified={verified} pairs={total_p} states={result.n_states} | "
                          f"{thm.name[:40]} ({elapsed:.1f}s) | {mem_info}{mem_warning}", flush=True)
                if debug_mem:
                    _log_memory_breakdown(worker_id, f"after_theorem_{i+1}_{thm.name[:30]}")
                if debug_tracemalloc:
                    import tracemalloc
                    snap = tracemalloc.take_snapshot()
                    diff = snap.compare_to(_tracemalloc_prev_snap, "lineno")
                    total_diff_mb = sum(s.size_diff for s in diff if s.size_diff > 0) / (1024 * 1024)
                    print(f"  [W{worker_id} TRACEMALLOC] после теоремы {i+1} ({thm.name[:30]}) | прирост ~{total_diff_mb:.0f} MB, топ по size_diff:", flush=True)
                    shown = 0
                    for s in diff:
                        if s.size_diff <= 0 or shown >= 15:
                            continue
                        mb = s.size_diff / (1024 * 1024)
                        loc = s.traceback[0] if s.traceback else "?"
                        print(f"    +{mb:.1f} MB  {loc}", flush=True)
                        shown += 1
                    _tracemalloc_prev_snap = snap

                consecutive_errors = 0  # Сброс при успехе

                # Очистка result — state_dict и pairs больше не нужны
                del result
                del filtered_pairs
                del pairs_dicts
                import gc
                gc.collect()

                # Garbage collection в Lean — освобождаем deleted goal states
                if GC_INTERVAL > 0 and (i + 1) % GC_INTERVAL == 0:
                    try:
                        dojo.server.gc()
                    except Exception:
                        pass  # gc() может упасть если сервер уже мёртв

                # Логируем после всех очисток
                _log_to_file(f"    MEM AFTER cleanup+gc: {_get_full_mem_info()}")
                _log_to_file(f"<<< FINISHED theorem {i+1}/{n_thms}: {thm.name}")

                # Периодический перезапуск dojo для полной очистки памяти Lean
                if RESTART_INTERVAL > 0 and (i + 1) % RESTART_INTERVAL == 0 and (i + 1) < len(theorems):
                    _log_to_file(f"!!! RESTARTING dojo (every {RESTART_INTERVAL} theorems)")
                    _log_to_file(f"    MEM BEFORE dojo.stop(): {_get_full_mem_info()}")
                    print(f"  [W{worker_id}] Перезапуск dojo (каждые {RESTART_INTERVAL} теорем) для очистки памяти...")
                    try:
                        dojo.stop()
                    except Exception as e:
                        _log_to_file(f"    WARN: dojo.stop() raised: {e}")
                    # Даём время процессу завершиться
                    time.sleep(1)
                    gc.collect()
                    _log_to_file(f"    MEM AFTER dojo.stop() + gc: {_get_full_mem_info()}")
                    dojo = _create_dojo()
                    explorer = _create_explorer(dojo)
                    _log_to_file(f"    MEM AFTER new dojo started: {_get_full_mem_info()}")
                    if debug_mem:
                        _log_memory_breakdown(worker_id, f"after_dojo_restart_{i+1}")

            except Exception as e:
                elapsed = time.time() - t0
                consecutive_errors += 1
                err_str = str(e)[:200]
                worker_results.append({
                    "theorem": thm.name, "proven": False,
                    "error": err_str[:80], "pairs": 0,
                    "states": 0, "steps": 0, "time": elapsed,
                })
                _log_to_file(f"!!! ERROR on theorem {i+1}/{n_thms}: {thm.name}")
                _log_to_file(f"    Error: {err_str}")
                _log_to_file(f"    MEM at error: {_get_full_mem_info()}")
                _diag(
                    "theorem_error",
                    theorem=thm.name,
                    theorem_idx=i + 1,
                    error=err_str[:1000],
                    elapsed=round(elapsed, 3),
                    mem=_get_full_mem_info(),
                )
                print(f"  [W{worker_id}] ERROR: {thm.name[:35]} | {err_str[:60]}")

                # Garbage collection даже после ошибки
                try:
                    dojo.server.gc()
                except Exception:
                    pass

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(f"  [W{worker_id}] ⚠ {consecutive_errors} ошибок подряд — "
                          f"Lean/Pantograph вероятно упал (PANIC). Пробуем перезапустить dojo...")
                    try:
                        dojo.stop()
                    except Exception:
                        pass
                    try:
                        dojo = _create_dojo()
                        explorer = _create_explorer(dojo)
                        consecutive_errors = 0  # Сброс после успешного перезапуска
                        print(f"  [W{worker_id}] Dojo перезапущен, продолжаем.")
                    except Exception as restart_err:
                        print(f"  [W{worker_id}] Не удалось перезапустить dojo: {restart_err}. Прерываем worker.")
                        break

    finally:
        try:
            dojo.stop()
        except Exception:
            pass

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
        sft = []
        for p in pairs_dicts:
            # Пропускаем negative examples (пустой tactic)
            tactic = p.get("tactic", "")
            if not tactic or not tactic.strip():
                continue
            thm_stmt = p.get("theorem_statement", "")
            input_text = f"Theorem to prove: {thm_stmt}\n\nCurrent proof state:\n{p['state']}" if thm_stmt else f"Current proof state:\n{p['state']}"
            sft.append({
                "instruction": "You are a Lean 4 theorem prover. Given the theorem and current proof state, suggest the next tactic.",
                "input": input_text,
                "output": tactic,
            })
        with open(f, "w") as fh:
            json.dump(sft, fh, indent=2, ensure_ascii=False)
    elif fmt == "chat":
        f = output_dir / f"lean_chat_{ts}.json"
        chat = []
        for p in pairs_dicts:
            # Пропускаем negative examples (пустой tactic)
            tactic = p.get("tactic", "")
            if not tactic or not tactic.strip():
                continue
            thm_stmt = p.get("theorem_statement", "")
            if thm_stmt:
                user_content = f"I want to prove: {thm_stmt}\n\nCurrent proof state:\n```\n{p['state']}\n```\n\nWhat tactic should I apply?"
            else:
                user_content = f"Prove this goal:\n```\n{p['state']}\n```"
            chat.append({
                "messages": [
                    {"role": "system", "content": "You are an expert Lean 4 theorem prover. Given a theorem and proof state, suggest the next tactic."},
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": tactic},
                ]
            })
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

    pp_full = not getattr(args, "no_pp_full", False)
    with PantographDojo(project_path=str(REPO_DIR), imports=["Mathlib"],
                        pp_full=pp_full) as dojo:
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
    ray_kwargs = {
        # Ограничиваем object store до 2GB чтобы не съедал RAM
        "object_store_memory": 2 * 1024 * 1024 * 1024,
    }
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
    log_dir = NAV_DATA.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    print(f"\nЗапуск {n_workers} workers...")
    print(f"  ЛОГИ для диагностики OOM: {log_dir}/worker_*.log")
    print("=" * 60)

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
    if args.decompose_auto:
        print(f"  Декомпозиция automation: ВКЛ (simp→rw шаги)")
    print(f"  Макс пар на worker: {args.max_pairs_per_worker}")
    print(f"  Макс состояний на теорему: {args.max_states_per_theorem} (ограничение памяти BFS)")
    if not pp_full:
        print(f"  pp_full: ВЫКЛ (компактный вывод)")
    if args.debug_mem:
        print(f"  debug-mem: ВКЛ (разбивка памяти self/дочерние после каждой теоремы)")
    if args.debug_tracemalloc:
        print(f"  debug-tracemalloc: ВКЛ (топ аллокаций Python после каждой теоремы)")
    print(f"  gc-interval: {args.gc_interval} (вызов Lean gc() каждые N теорем)")
    if args.restart_interval > 0:
        print(f"  restart-interval: {args.restart_interval} (перезапуск dojo каждые N теорем для очистки памяти)")
    else:
        print("  restart-interval: 0 (перезапуск dojo отключён)")
    min_fg = getattr(args, "min_free_gb", 12.0)
    if min_fg > 0:
        print(f"  min-free-gb: {min_fg} (пропуск теоремы если свободной RAM < {min_fg} GB)")
    max_rss = getattr(args, "max_worker_rss_mb", 7500)
    if max_rss > 0:
        print(f"  max-worker-rss-mb: {max_rss} (досрочное завершение BFS по текущей теореме при превышении)")
    max_tac_jump = getattr(args, "max_tactic_rss_jump_mb", 0)
    if max_tac_jump > 0:
        print(f"  max-tactic-rss-jump-mb: {max_tac_jump} (стоп при аномальном скачке памяти на одной тактике)")
    if args.diag_jsonl:
        print("  diag-jsonl: ВКЛ (worker_*.jsonl с фазами BFS и run_tac)")
    if args.trace_every_tac:
        tr = args.trace_theorem if args.trace_theorem else "<ALL>"
        print(f"  trace-every-tac: ВКЛ (теоремы: {tr})")
    # Подсказка: при 5 воркерах и 62GB лучше не съедать >40GB воркерами, иначе много SKIP
    if max_rss > 0 and n_workers > 0:
        approx_gb = (n_workers * max_rss) / 1024
        print(f"  (при {n_workers} воркерах макс ~{approx_gb:.0f} GB под воркеры; при частых SKIP попробуйте --workers 3 или --min-free-gb 8)")

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
            banned_tactics=banned if banned else None,
            decompose_auto=args.decompose_auto,
            min_proof_length=args.min_proof_length,
            pp_full=pp_full,
            max_pairs_per_worker=args.max_pairs_per_worker,
            max_states_per_theorem=args.max_states_per_theorem,
            debug_mem=args.debug_mem,
            debug_tracemalloc=args.debug_tracemalloc,
            gc_interval=args.gc_interval,
            restart_interval=args.restart_interval,
            min_free_gb=getattr(args, "min_free_gb", 12.0),
            max_worker_rss_mb=getattr(args, "max_worker_rss_mb", 7500),
            max_tactic_rss_jump_mb=getattr(args, "max_tactic_rss_jump_mb", 0),
            diag_jsonl=bool(getattr(args, "diag_jsonl", False)),
            trace_theorem=getattr(args, "trace_theorem", ""),
            trace_every_tac=bool(getattr(args, "trace_every_tac", False)),
        )
        futures.append(future)

    # Собираем результаты по мере готовности
    all_pairs = []
    all_results = []

    # Мониторинг памяти системы
    def _log_system_memory():
        try:
            import psutil
            vm = psutil.virtual_memory()
            used_gb = vm.used / (1024**3)
            total_gb = vm.total / (1024**3)
            avail_gb = vm.available / (1024**3)
            pct = vm.percent
            return f"RAM: {used_gb:.1f}/{total_gb:.1f} GB ({pct:.0f}% used, {avail_gb:.1f} GB free)"
        except:
            return "RAM: N/A"

    remaining = list(futures)
    last_mem_log = 0
    while remaining:
        done, remaining = ray.wait(remaining, num_returns=1, timeout=10.0)

        # Логируем память каждые 30 секунд или при завершении worker'а
        import time as _time
        now = _time.time()
        if done or (now - last_mem_log > 30):
            print(f"  [{_log_system_memory()}] Workers running: {len(remaining)}")
            last_mem_log = now

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
                err_msg = str(e)
                if "Worker unexpectedly exits" in err_msg or "connection error" in err_msg.lower():
                    print(f"\n  Worker убит (OOM или паника Lean/pantograph). Обычные причины: "
                          f"OOM killer, PANIC в pantograph-repl (unreachable code / declRangeExt). "
                          f"См. лог выше: последняя напечатанная теорема — та, на которой упало.")
                print(f"  Worker ОШИБКА: {e}")

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
