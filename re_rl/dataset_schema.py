"""
JSON Schema definitions for generated datasets.
"""

from __future__ import annotations

from typing import Dict, Any


MESSAGE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["role", "content"],
    "properties": {
        "role": {"type": "string", "enum": ["system", "user", "assistant"]},
        "content": {"type": "string"},
    },
    "additionalProperties": False,
}


SCHEMA_PRETRAIN: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["text"],
    "properties": {
        "text": {"type": "string"},
        "metadata": {"type": "object"},
    },
    "additionalProperties": True,
}


SCHEMA_CHAT: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["messages"],
    "properties": {
        "messages": {
            "type": "array",
            "minItems": 2,
            "items": MESSAGE_SCHEMA,
        },
        "metadata": {"type": "object"},
    },
    "additionalProperties": True,
}


SCHEMA_SFT_LEGACY: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["instruction", "input", "output"],
    "properties": {
        "instruction": {"type": "string"},
        "input": {"type": "string"},
        "output": {"type": "string"},
        "metadata": {"type": "object"},
    },
    "additionalProperties": True,
}


SCHEMA_GRPO: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["question", "answer", "metadata"],
    "properties": {
        "question": {"type": "string"},
        "answer": {"type": "string"},
        "task_type": {"type": "string"},
        "difficulty": {"type": "integer"},
        "language": {"type": "string"},
        "metadata": {
            "type": "object",
            "required": ["task_type", "difficulty", "language", "ref_final_answer"],
            "properties": {
                "task_type": {"type": "string"},
                "difficulty": {"type": "integer"},
                "language": {"type": "string"},
                "output_format": {"type": "string"},
                "reasoning_mode": {"type": "boolean"},
                "ref_final_answer": {"type": "string"},
            },
            "additionalProperties": True,
        },
    },
    "additionalProperties": True,
}


DATASET_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "pretrain": SCHEMA_PRETRAIN,
    "sft": SCHEMA_SFT_LEGACY,
    "chat": SCHEMA_CHAT,
    "sft_chat": SCHEMA_CHAT,
    "grpo": SCHEMA_GRPO,
}
