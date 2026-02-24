"""
Dataset validation against JSON Schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator

from re_rl.dataset_schema import DATASET_SCHEMAS


def infer_dataset_format(sample: Dict[str, Any]) -> str:
    """Infer dataset format from sample keys."""
    if "text" in sample:
        return "pretrain"
    if "question" in sample and "answer" in sample:
        return "grpo"
    if "messages" in sample:
        return "chat"
    if "instruction" in sample and "input" in sample and "output" in sample:
        return "sft"
    raise ValueError("Unable to infer dataset format from sample keys")


def validate_record(record: Dict[str, Any], dataset_format: str) -> Optional[str]:
    """Validate one record. Returns None if valid, otherwise error text."""
    schema = DATASET_SCHEMAS.get(dataset_format)
    if schema is None:
        return f"Unknown dataset format '{dataset_format}'"

    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(record))
    if not errors:
        return None
    # Return first error in compact readable style
    err = errors[0]
    path = ".".join(str(p) for p in err.path) or "<root>"
    return f"{path}: {err.message}"


def validate_dataset(
    dataset: List[Dict[str, Any]],
    dataset_format: Optional[str] = None,
) -> str:
    """
    Validate full dataset and return resolved dataset_format.

    Raises:
        ValueError: when dataset is invalid or format is unknown.
    """
    if not dataset:
        raise ValueError("Dataset is empty")

    resolved_format = dataset_format or infer_dataset_format(dataset[0])
    if resolved_format not in DATASET_SCHEMAS:
        raise ValueError(f"Unknown dataset format '{resolved_format}'")

    for idx, record in enumerate(dataset):
        err = validate_record(record, resolved_format)
        if err is not None:
            raise ValueError(f"Invalid record at index {idx}: {err}")

    return resolved_format
