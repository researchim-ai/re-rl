"""TrialGapTask — сравнение двух пробных функций по Рэлею.

Меньшая средняя энергия не видна по одному числителю: нормы разные, поэтому сравниваются произведения.
Число узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _apply(psi: Sequence[int], potential: Sequence[int], index: int) -> int:
    left = psi[index - 1] if index else 0
    right = psi[index + 1] if index + 1 < len(psi) else 0
    center = psi[index]
    return -left + 2 * center - right + potential[index] * center


def trial_trace(first: Sequence[int], second: Sequence[int],
                potential: Sequence[int]) -> Tuple[List[Tuple[int, int]], int]:
    num1 = num2 = 0
    norm1 = norm2 = 0
    trace = []
    for index in range(len(first)):
        num1 += first[index] * _apply(first, potential, index)
        num2 += second[index] * _apply(second, potential, index)
        norm1 += first[index] * first[index]
        norm2 += second[index] * second[index]
        trace.append((num1, num2))
    gap = num1 * norm2 - num2 * norm1
    return trace, gap


class TrialGapTask(BaseMathTask):
    TASK_TYPE = "trial_gap"
    TASK_TYPES = ["gap", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.first = [random.randint(-2, 2) for _ in range(self.n)]
        self.second = [random.randint(-2, 2) for _ in range(self.n)]
        if not any(self.first):
            self.first[0] = 1
        if not any(self.second):
            self.second[0] = 1
        self.potential = [random.randint(-2, 3) for _ in range(self.n)]
        self.trace, self.gap = trial_trace(self.first, self.second, self.potential)
        self.num1 = self.trace[-1][0]
        self.answer = self.gap if self.task_type == "gap" else self.num1
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "gap" else "s1"
        return texts.t(
            key, language, n=self.n, first=self._row(self.first),
            second=self._row(self.second), potential=self._row(self.potential),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, first=first, second=second)
            for index, (first, second) in enumerate(self.trace, 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
