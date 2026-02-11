"""
Shared dataset save utilities for formal pipelines.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable


def save_pairs_dataset(
    pairs_dicts: Iterable[Dict],
    output_dir,
    fmt: str,
    metadata: Dict,
    dataset_prefix: str = "lean_data",
    metadata_prefix: str = "metadata",
) -> Path:
    """
    Save dataset rows (dicts) in one of supported formats.

    Supported formats:
      - jsonl
      - json
      - sft
      - chat
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rows = list(pairs_dicts)

    if fmt == "jsonl":
        out = output_dir / f"{dataset_prefix}_{ts}.jsonl"
        with open(out, "w") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    elif fmt == "json":
        out = output_dir / f"{dataset_prefix}_{ts}.json"
        with open(out, "w") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    elif fmt == "sft":
        out = output_dir / f"{dataset_prefix.replace('data', 'sft')}_{ts}.json"
        sft = []
        for row in rows:
            tactic = (row.get("tactic") or "").strip()
            if not tactic:
                continue
            thm_stmt = row.get("theorem_statement", "")
            state = row.get("state", "")
            input_text = (
                f"Theorem to prove: {thm_stmt}\n\nCurrent proof state:\n{state}"
                if thm_stmt
                else f"Current proof state:\n{state}"
            )
            sft.append(
                {
                    "instruction": (
                        "You are a Lean 4 theorem prover. Given the theorem and current proof "
                        "state, suggest the next tactic."
                    ),
                    "input": input_text,
                    "output": tactic,
                }
            )
        with open(out, "w") as f:
            json.dump(sft, f, indent=2, ensure_ascii=False)
    elif fmt == "chat":
        out = output_dir / f"{dataset_prefix.replace('data', 'chat')}_{ts}.json"
        chat = []
        for row in rows:
            tactic = (row.get("tactic") or "").strip()
            if not tactic:
                continue
            thm_stmt = row.get("theorem_statement", "")
            state = row.get("state", "")
            if thm_stmt:
                user_content = (
                    f"I want to prove: {thm_stmt}\n\nCurrent proof state:\n```\n{state}\n```"
                    "\n\nWhat tactic should I apply?"
                )
            else:
                user_content = f"Prove this goal:\n```\n{state}\n```"
            chat.append(
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert Lean 4 theorem prover. Given a theorem and "
                                "proof state, suggest the next tactic."
                            ),
                        },
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": tactic},
                    ]
                }
            )
        with open(out, "w") as f:
            json.dump(chat, f, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Unsupported dataset format: {fmt}")

    meta = output_dir / f"{metadata_prefix}_{ts}.json"
    with open(meta, "w") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

    print(f"  Датасет:    {out}  ({out.stat().st_size:,} bytes)")
    print(f"  Метаданные: {meta}")
    return out
