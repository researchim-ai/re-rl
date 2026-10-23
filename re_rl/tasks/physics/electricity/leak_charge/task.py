"""LeakChargeTask — утечка заряда целыми долями.

На шаге утекает частное заряда и делителя, заряд уменьшается на эту утечку.
Сумма остатка и утечек равна начальному заряду. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def leak_trace(charge: int, divisors: Sequence[int]) -> List[Tuple[int, int]]:
    leaked = 0
    trace = []
    for divisor in divisors:
        lost = charge // divisor
        charge -= lost
        leaked += lost
        trace.append((charge, leaked))
    return trace


class LeakChargeTask(BaseMathTask):
    TASK_TYPE = "leak_charge"
    TASK_TYPES = ["left", "leaked"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "q": 30}, 2: {"n": 2, "q": 40}, 3: {"n": 3, "q": 50},
        4: {"n": 4, "q": 60}, 5: {"n": 5, "q": 80}, 6: {"n": 6, "q": 90},
        7: {"n": 7, "q": 100}, 8: {"n": 8, "q": 120}, 9: {"n": 10, "q": 140},
        10: {"n": 12, "q": 160},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.charge0 = random.randint(self.n, max(self.n, int(p["q"])))
        self.divisors = [random.randint(2, 6) for _ in range(self.n)]
        self.trace = leak_trace(self.charge0, self.divisors)
        self.left, self.leaked = self.trace[-1]
        self.answer = self.left if self.task_type == "left" else self.leaked
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.divisors)
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(key, language, charge=self.charge0, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, divisor=divisor, left=left, leaked=leaked)
            for index, (divisor, (left, leaked)) in enumerate(zip(self.divisors, self.trace), 1)
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
