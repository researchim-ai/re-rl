#!/usr/bin/env python3
"""
Deep-profile запуск генерации данных Lean BFS.

Идея: тот же run_bfs_parallel.py, но с пресетом, который смещает датасет
в сторону более длинных траекторий доказательства.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deep-profile обёртка над run_bfs_parallel.py",
    )
    # Базовые параметры запуска
    parser.add_argument("--mathlib-version", default="v4.26.0")
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--max-theorems", type=int, default=1000)
    parser.add_argument("--output-dir", default="datasets/formal_math_data_deep")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--verbose", action="store_true")

    # Deep-параметры (по умолчанию «глубже», чем стандарт)
    parser.add_argument("--max-steps", type=int, default=15000,
                        help="Бюджет шагов на теорему (deep default: 15000)")
    parser.add_argument("--max-time", type=int, default=180,
                        help="Время на теорему в секундах (deep default: 180)")
    parser.add_argument("--max-states-per-theorem", type=int, default=6000,
                        help="Лимит состояний на теорему (deep default: 6000)")
    parser.add_argument("--min-proof-length", type=int, default=4,
                        help="Оставлять только пары с distance_to_proof >= N")

    # Память/стабильность
    parser.add_argument("--min-free-gb", type=float, default=10.0)
    parser.add_argument("--max-worker-rss-mb", type=int, default=8000)
    parser.add_argument("--max-tactic-rss-jump-mb", type=int, default=0)

    # Тактики: мягкий бан быстрых «замыканий», чтобы чаще получать multi-step
    parser.add_argument(
        "--ban-tactics",
        default="trivial,tauto,decide,omega",
        help="Список root-тактик через запятую",
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Агрессивный deep-режим: включает --no-auto в базовом скрипте",
    )

    # Диагностика
    parser.add_argument("--diag-jsonl", action="store_true")
    parser.add_argument("--trace-theorem", default="")
    parser.add_argument("--trace-every-tac", action="store_true")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script = Path(__file__).resolve().parent / "run_bfs_parallel.py"

    cmd = [
        sys.executable,
        str(script),
        "--mathlib-version", args.mathlib_version,
        "--num-workers", str(args.num_workers),
        "--max-theorems", str(args.max_theorems),
        "--output-dir", args.output_dir,
        "--seed", str(args.seed),
        "--max-steps", str(args.max_steps),
        "--max-time", str(args.max_time),
        "--max-states-per-theorem", str(args.max_states_per_theorem),
        "--min-proof-length", str(args.min-proof_length),
        "--min-free-gb", str(args.min_free_gb),
        "--max-worker-rss-mb", str(args.max_worker_rss_mb),
        "--max-tactic-rss-jump-mb", str(args.max_tactic_rss_jump_mb),
        "--gc-interval", "1",
        "--restart-interval", "0",
        "--no-early-stop",
        "--decompose-auto",
    ]

    if args.verbose:
        cmd.append("--verbose")
    if args.ban_tactics.strip():
        cmd.extend(["--ban-tactics", args.ban_tactics])
    if args.aggressive:
        cmd.append("--no-auto")
    if args.diag_jsonl:
        cmd.append("--diag-jsonl")
    if args.trace_theorem.strip():
        cmd.extend(["--trace-theorem", args.trace_theorem])
    if args.trace_every_tac:
        cmd.append("--trace-every-tac")

    print("Deep run command:")
    print(" ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
