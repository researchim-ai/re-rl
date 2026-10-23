"""TotientRowTask — решето функции Эйлера.

phi(1) = 1. Если phi(i) всё ещё равно i, i простое, и у каждого кратного
phi заменяется на phi/p*(p-1). Верхняя граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def totient_values(limit: int) -> List[int]:
    phi = list(range(limit + 1))
    for i in range(2, limit + 1):
        if phi[i] == i:
            for j in range(i, limit + 1, i):
                phi[j] = phi[j] // i * (i - 1)
    return phi


class TotientRowTask(BaseMathTask):
    TASK_TYPE = "totient_row"
    TASK_TYPES = ["phi", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 6}, 3: {"n": 8}, 4: {"n": 10},
        5: {"n": 12}, 6: {"n": 15}, 7: {"n": 18}, 8: {"n": 22},
        9: {"n": 26}, 10: {"n": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.phi_row = totient_values(self.n)
        self.phi = self.phi_row[self.n]
        self.total = sum(self.phi_row[1:])
        self.answer = self.phi if self.task_type == "phi" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "phi" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        running = 0
        steps = []
        for number, value in enumerate(self.phi_row):
            if number == 0:
                continue
            running += value
            steps.append(texts.t("s2", self.language, i=number, phi=value, total=running))
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
