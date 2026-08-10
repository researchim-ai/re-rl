"""Smoke-тест: verify(эталон) == 1.0 для КАЖДОГО зарегистрированного типа задач.

Ловит регрессии в логике проверки ответов сразу по всем типам: если для
какого-то типа собственный эталонный ответ перестаёт засчитываться, тест падает.
"""

import random

import numpy as np
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", sorted(ALL_TASK_GENERATORS.keys()))
def test_verify_accepts_own_answer(task_type):
    random.seed(0)
    np.random.seed(0)

    gen = ALL_TASK_GENERATORS[task_type]
    task = gen(language="ru", difficulty=3)
    if task.final_answer is None:
        task.get_result()

    prediction = f"<answer>{task.final_answer}</answer>"
    score = task.verify(prediction)
    assert score == pytest.approx(1.0), (
        f"verify() не засчитал собственный эталон для '{task_type}': "
        f"score={score}, answer={task.final_answer!r}"
    )
