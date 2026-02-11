#!/usr/bin/env python3
"""
Полный guided-pipeline для более глубоких доказательств.

Отдельный режим от BFS:
1) Загружает теоремы из Lean env
2) Запускает best-first guided search (policy/value эвристики)
3) Сохраняет датасет training pairs
"""

import argparse
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from re_rl.tasks.formal.dataset_io import save_pairs_dataset
from re_rl.tasks.formal.rag_io import load_or_build_rag, load_or_build_templates


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Guided proof-search pipeline")
    p.add_argument("--search-mode", default="mcts", choices=["best_first", "mcts"])
    p.add_argument("--mathlib-version", default="v4.26.0")
    p.add_argument("--max-theorems", type=int, default=200)
    p.add_argument("--max-steps", type=int, default=12000)
    p.add_argument("--max-time", type=int, default=180)
    p.add_argument("--max-states", type=int, default=6000)
    p.add_argument("--max-depth", type=int, default=12)
    p.add_argument("--candidate-top-k", type=int, default=96)
    p.add_argument("--max-total-tactics-per-state", type=int, default=192)
    p.add_argument("--max-tactics-per-template", type=int, default=50)
    p.add_argument("--auto-tactics-after-depth", type=int, default=3)
    p.add_argument("--negatives-per-state", type=int, default=2)
    p.add_argument("--mcts-iters", type=int, default=2000)
    p.add_argument("--mcts-c-puct", type=float, default=1.4)
    p.add_argument("--mcts-gamma", type=float, default=0.97)
    p.add_argument("--mcts-depth-schedule", default="6,10,14",
                   help="Iterative deepening depths для MCTS, через запятую (пусто=без расписания)")
    p.add_argument("--mcts-log-top-actions", type=int, default=5,
                   help="Сколько top root-экшенов MCTS печатать по visit count")
    p.add_argument("--min-proof-length", type=int, default=4)
    p.add_argument("--ban-tactics", default="trivial,tauto,decide,omega")
    p.add_argument("--rag-model", default="sbert")
    p.add_argument("--min-template-freq", type=int, default=3)
    p.add_argument("--output-dir", default="datasets/formal_math_data_guided")
    p.add_argument("--output-format", default="jsonl", choices=["jsonl", "json"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def _ensure_path_env() -> None:
    os.environ["PATH"] = str(Path.home() / ".elan" / "bin") + ":" + os.environ.get("PATH", "")


def _parse_depth_schedule(text: str, max_depth: int) -> list[int]:
    raw = [x.strip() for x in (text or "").split(",") if x.strip()]
    if not raw:
        return []
    vals = []
    for x in raw:
        try:
            v = int(x)
        except ValueError:
            continue
        if v > 0:
            vals.append(min(v, max_depth))
    vals = sorted(set(vals))
    if not vals:
        return []
    if vals[-1] != max_depth:
        vals.append(max_depth)
    return vals


def save_dataset(pairs: list[dict], output_dir: Path, fmt: str, metadata: dict) -> Path:
    return save_pairs_dataset(
        pairs,
        output_dir,
        fmt,
        metadata,
        dataset_prefix="lean_guided",
        metadata_prefix="metadata_guided",
    )


def main() -> int:
    args = parse_args()
    random.seed(args.seed)
    _ensure_path_env()

    from re_rl.tasks.formal.guided_pipeline import (
        GuidedSearchConfig,
        GuidedSearchExplorer,
        MCTSConfig,
        MCTSSearchExplorer,
    )
    from re_rl.tasks.formal.lean_navigator import (
        PantographDojo,
        load_theorems_from_env,
    )

    cache = Path.home() / ".cache" / "re_rl" / f"mathlib4-{args.mathlib_version}"
    repo_dir = cache / "mathlib4"
    nav_data = cache / "navigator_data"
    output_dir = Path(args.output_dir)

    print("=" * 60)
    print("  GUIDED PROOF SEARCH PIPELINE")
    print("=" * 60)
    print(f"  Mathlib:        {args.mathlib_version}")
    print(f"  Theorems:       {args.max_theorems}")
    print(f"  max-steps:      {args.max_steps}")
    print(f"  max-time:       {args.max_time}")
    print(f"  max-depth:      {args.max_depth}")
    print(f"  candidate-topk: {args.candidate_top_k}")
    print(f"  search-mode:    {args.search_mode}")
    if args.search_mode == "mcts":
        print(f"  mcts-iters:     {args.mcts_iters}")
        print(f"  mcts-c-puct:    {args.mcts_c_puct}")
        print(f"  mcts-gamma:     {args.mcts_gamma}")
        print(f"  depth-schedule: {args.mcts_depth_schedule or '<disabled>'}")
    print(f"  output:         {output_dir}")

    if not (repo_dir.parent / ".step_5_done").exists():
        print(f"ОШИБКА: Трейсинг не выполнен для {args.mathlib_version}")
        return 1

    extractor = load_or_build_templates(nav_data=nav_data, repo_dir=repo_dir, print_fn=print)
    rag = load_or_build_rag(
        extractor=extractor,
        nav_data=nav_data,
        rag_model=args.rag_model,
        min_template_freq=args.min_template_freq,
    )

    banned = {t.strip() for t in args.ban_tactics.split(",") if t.strip()}
    common_cfg = dict(
        max_steps=args.max_steps,
        max_time=args.max_time,
        max_states=args.max_states,
        max_depth=args.max_depth,
        candidate_top_k=args.candidate_top_k,
        max_total_tactics_per_state=args.max_total_tactics_per_state,
        max_tactics_per_template=args.max_tactics_per_template,
        auto_tactics_after_depth=args.auto_tactics_after_depth,
        negatives_per_state=args.negatives_per_state,
        banned_tactics=banned if banned else None,
    )

    all_pairs = []
    theorem_results = []

    with PantographDojo(project_path=str(repo_dir), imports=["Mathlib"], pp_full=True) as dojo:
        theorems = load_theorems_from_env(
            dojo=dojo,
            module_prefix="Mathlib",
            max_theorems=args.max_theorems if args.max_theorems > 0 else 5000,
            cache_dir=str(nav_data),
            verbose=args.verbose,
            validate_goals=True,
        )
        print(f"Загружено теорем: {len(theorems)}")

        depth_schedule = _parse_depth_schedule(args.mcts_depth_schedule, args.max_depth)
        if args.search_mode == "best_first":
            cfg = GuidedSearchConfig(**common_cfg)
            explorer = GuidedSearchExplorer(dojo=dojo, rag=rag, config=cfg, verbose=args.verbose)
        else:
            explorer = None
        for i, thm in enumerate(theorems, start=1):
            if args.search_mode == "best_first":
                result = explorer.search(
                    theorem_name=thm.name,
                    theorem_goal_expr=thm.goal_expr,
                    theorem_code=thm.goal_state,
                )
            else:
                stages = depth_schedule if depth_schedule else [args.max_depth]
                result = None
                depth_used = None
                for d in stages:
                    stage_cfg = dict(common_cfg)
                    stage_cfg["max_depth"] = d
                    cfg = MCTSConfig(
                        **stage_cfg,
                        mcts_iters=args.mcts_iters,
                        mcts_c_puct=args.mcts_c_puct,
                        mcts_gamma=args.mcts_gamma,
                    )
                    mcts = MCTSSearchExplorer(dojo=dojo, rag=rag, config=cfg, verbose=args.verbose)
                    stage_result = mcts.search(
                        theorem_name=thm.name,
                        theorem_goal_expr=thm.goal_expr,
                        theorem_code=thm.goal_state,
                    )
                    result = stage_result
                    depth_used = d
                    if args.verbose:
                        stats = stage_result.search_stats or {}
                        print(
                            f"    [MCTS depth={d}] proven={stage_result.theorem_proven} "
                            f"steps={stage_result.n_steps} states={stage_result.n_states} "
                            f"iters={stats.get('iterations', 0)}"
                        )
                    if stage_result.theorem_proven:
                        break
                if result and result.search_stats is not None:
                    result.search_stats["depth_used"] = depth_used

            # Фильтрация по длине доказательства, если есть proof-путь.
            filtered = []
            for p in result.pairs:
                if p.distance_to_proof < 0:
                    filtered.append(p)
                elif p.distance_to_proof >= args.min_proof_length:
                    filtered.append(p)

            for p in filtered:
                all_pairs.append(
                    {
                        "state": p.state,
                        "tactic": p.tactic,
                        "next_state": p.next_state,
                        "distance_to_proof": p.distance_to_proof,
                        "theorem_name": p.theorem_name,
                        "theorem_statement": p.theorem_statement,
                    }
                )

            theorem_results.append(
                {
                    "theorem": thm.name,
                    "proven": result.theorem_proven,
                    "steps": result.n_steps,
                    "states": result.n_states,
                    "pairs": len(filtered),
                    "proof_length": len(result.proof_tactics),
                    "max_depth_reached": result.max_depth_reached,
                    "time": round(result.elapsed, 3),
                    "search_stats": result.search_stats or {},
                }
            )

            if result.theorem_proven or i % 10 == 0:
                proven = sum(1 for r in theorem_results if r["proven"])
                total_pairs = sum(r["pairs"] for r in theorem_results)
                print(
                    f"  [{i}/{len(theorems)}] "
                    f"proven={proven} pairs={total_pairs} "
                    f"last_steps={result.n_steps} last_depth={result.max_depth_reached} "
                    f"| {thm.name[:55]}"
                )
                if args.search_mode == "mcts" and result.search_stats:
                    topn = max(0, args.mcts_log_top_actions)
                    top_actions = (result.search_stats.get("root_top_actions") or [])[:topn]
                    if top_actions:
                        summary = ", ".join(
                            f"{x['tactic'][:32]}(v={x['visits']},q={x['q']})"
                            for x in top_actions
                        )
                        print(f"    MCTS top actions: {summary}")
            elif args.search_mode == "mcts" and args.verbose and result.search_stats:
                topn = max(0, args.mcts_log_top_actions)
                top_actions = (result.search_stats.get("root_top_actions") or [])[:topn]
                if top_actions:
                    summary = ", ".join(
                        f"{x['tactic'][:32]}(v={x['visits']},q={x['q']})"
                        for x in top_actions
                    )
                    print(f"    MCTS top actions: {summary}")

    proven = sum(1 for r in theorem_results if r["proven"])
    total_pairs = len(all_pairs)
    print("\n" + "=" * 60)
    print("  ИТОГО (GUIDED)")
    print("=" * 60)
    print(f"  Теорем:     {len(theorem_results)}")
    print(f"  Доказано:   {proven}")
    print(f"  Пары:       {total_pairs}")

    metadata = {
        "generation_date": datetime.now().isoformat(),
        "mathlib_version": args.mathlib_version,
        "mode": f"guided_{args.search_mode}",
        "config": vars(args),
        "summary": {
            "theorems": len(theorem_results),
            "proven": proven,
            "pairs": total_pairs,
        },
        "theorem_results": theorem_results,
    }
    save_dataset(all_pairs, output_dir, args.output_format, metadata)
    return 0 if proven > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
