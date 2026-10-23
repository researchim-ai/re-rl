"""PellRowTask — числа Пелля и соседняя последовательность.

P(0) = 0, P(1) = 1, Q(0) = 1, Q(1) = 1. Дальше оба ряда удваивают предыдущий и прибавляют предпредыдущий.
Для каждого индекса Q^2 - 2*P^2 = (-1)^индекс. Индекс растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pell_trace(order: int) -> Tuple[List[int], List[int]]:
    pell = [0, 1]
    partner = [1, 1]
    for _ in range(2, order + 1):
        pell.append(2 * pell[-1] + pell[-2])
        partner.append(2 * partner[-1] + partner[-2])
    pell = pell[: order + 1]
    partner = partner[: order + 1]
    for index, (left, right) in enumerate(zip(pell, partner)):
        assert right * right - 2 * left * left == (-1) ** index
    return pell, partner


class PellRowTask(BaseMathTask):
    TASK_TYPE = "pell_row"
    TASK_TYPES = ["value", "partner"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 9}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.pell, self.partner = pell_trace(self.n)
        self.value = self.pell[-1]
        self.other = self.partner[-1]
        self.answer = self.value if self.task_type == "value" else self.other
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pell=left, partner=right)
            for index, (left, right) in enumerate(zip(self.pell, self.partner))
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
