"""Обёртка multiple-choice для любой задачи.

Позволяет превратить произвольную задачу re-rl в вопрос с вариантами ответа
(A, B, C, ...). Для числовых ответов дистракторы генерируются возмущением
правильного значения; для остальных — из ответов других задач того же типа.

Пример::

    from re_rl.tasks.generators import ALL_TASK_GENERATORS
    from re_rl.tasks.multiple_choice import to_multiple_choice, format_choice_prompt

    task = ALL_TASK_GENERATORS["arithmetic"](difficulty=3)
    mc = to_multiple_choice(task, num_options=4, seed=1)
    print(format_choice_prompt(mc))
    print(mc["correct_label"])  # напр. "C"
"""

from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional

from re_rl.rewards import coerce_float

LETTERS = "ABCDEFGHIJ"


def _looks_integer(text: str, value: float) -> bool:
    return "." not in text and "e" not in text.lower() and float(value).is_integer()


def _format_number(value: float, integer_like: bool, decimals: int) -> str:
    if integer_like:
        return str(int(round(value)))
    return f"{value:.{decimals}f}"


def _numeric_distractors(value: float, text: str, n: int, rng: random.Random) -> List[str]:
    integer_like = _looks_integer(text, value)
    decimals = 0
    if not integer_like and "." in text:
        decimals = len(text.split(".")[-1])
        decimals = min(max(decimals, 1), 4)

    scale = max(abs(value), 1.0)
    seen = {round(value, 6)}
    out: List[str] = []
    attempts = 0
    while len(out) < n and attempts < 400:
        attempts += 1
        r = rng.random()
        if r < 0.45:
            cand = value + rng.choice([-3, -2, -1, 1, 2, 3])
        elif r < 0.75:
            cand = value * rng.choice([0.5, 2.0, 10.0, -1.0])
        else:
            cand = value + rng.uniform(-scale, scale)

        if integer_like:
            cand = round(cand)
        key = round(cand, 6)
        if key in seen:
            continue
        seen.add(key)
        out.append(_format_number(cand, integer_like, decimals))
    return out


def _same_type_distractors(task: Any, correct: str, n: int, rng: random.Random) -> List[str]:
    """Собирает дистракторы из ответов других задач того же типа."""
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    gen = ALL_TASK_GENERATORS.get(getattr(task, "TASK_TYPE", None))
    out: List[str] = []
    if gen is None:
        return out
    seen = {correct.strip()}
    for _ in range(n * 8):
        if len(out) >= n:
            break
        try:
            other = gen(language=getattr(task, "language", "ru"))
            if other.final_answer is None:
                other.get_result()
            ans = str(other.final_answer).strip()
        except Exception:
            continue
        if ans and ans not in seen:
            seen.add(ans)
            out.append(ans)
    return out


def to_multiple_choice(
    task: Any,
    num_options: int = 4,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Строит multiple-choice представление задачи.

    Args:
        task: любой экземпляр задачи (BaseTask) — будет решён при необходимости.
        num_options: общее число вариантов (включая правильный), 2..10.
        seed: сид для воспроизводимости.

    Returns:
        Словарь с полями: ``question``, ``options`` (список строк),
        ``labels`` (['A','B',...]), ``correct_index``, ``correct_label``,
        ``answer`` (правильное значение), ``task_type``.
    """
    rng = random.Random(seed)
    num_options = max(2, min(len(LETTERS), num_options))

    if task.final_answer is None:
        task.solve()
    correct = str(task.final_answer).strip()

    need = num_options - 1
    value = coerce_float(correct)
    if value is not None:
        distractors = _numeric_distractors(value, correct, need, rng)
    else:
        distractors = _same_type_distractors(task, correct, need, rng)

    # Если дистракторов не хватило — добиваем строковыми мутациями.
    idx = 1
    while len(distractors) < need:
        distractors.append(f"{correct} ({idx})")
        idx += 1

    options = distractors[:need] + [correct]
    rng.shuffle(options)
    correct_index = options.index(correct)

    return {
        "question": task.description,
        "options": options,
        "labels": list(LETTERS[:num_options]),
        "correct_index": correct_index,
        "correct_label": LETTERS[correct_index],
        "answer": correct,
        "task_type": getattr(task, "TASK_TYPE", None),
    }


def format_choice_prompt(mc: Dict[str, Any]) -> str:
    """Форматирует вопрос с вариантами в виде текста."""
    lines = [mc["question"], ""]
    for label, opt in zip(mc["labels"], mc["options"]):
        lines.append(f"{label}) {opt}")
    return "\n".join(lines)


def verify_choice(prediction: str, mc: Dict[str, Any]) -> float:
    """Оценивает ответ на multiple-choice: по букве или по значению."""
    from re_rl.rewards import extract_reasoning_and_answer

    _, answer = extract_reasoning_and_answer(prediction)
    text = (answer or prediction).strip()

    # 1) Буква варианта (A/B/...), возможно вида "B)" или "ответ: C".
    letter_match = re.search(r"\b([A-J])\b", text.upper())
    if letter_match:
        return 1.0 if letter_match.group(1) == mc["correct_label"] else 0.0

    # 2) Совпадение по значению.
    correct = mc["answer"]
    val = coerce_float(correct)
    if val is not None:
        pred_val = coerce_float(text)
        if pred_val is not None:
            import math
            return 1.0 if math.isclose(val, pred_val, rel_tol=1e-3, abs_tol=1e-6) else 0.0
    return 1.0 if text.lower() == str(correct).strip().lower() else 0.0
