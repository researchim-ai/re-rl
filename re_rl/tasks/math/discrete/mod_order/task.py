"""ModOrderTask — порядок основания по модулю.

Степень начинается с 1 и каждый шаг умножается на основание по модулю.
Основание взаимно просто с модулем, поэтому единица встретится.
Число умножений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def order_trace(base: int, modulus: int, steps: int) -> List[Tuple[int, int]]:
    power = 1
    order = 0
    trace = []
    for index in range(1, steps + 1):
        power = power * base % modulus
        if order == 0 and power == 1:
            order = index
        trace.append((power, order))
    return trace


class ModOrderTask(BaseMathTask):
    TASK_TYPE = "mod_order"
    TASK_TYPES = ["order", "power"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.modulus = self.n + 1
        self.base = random.randint(2, self.modulus - 1)
        while math.gcd(self.base, self.modulus) != 1:
            self.base = random.randint(2, self.modulus - 1)
        self.trace = order_trace(self.base, self.modulus, self.n)
        self.power, self.order = self.trace[-1]
        self.k = random.randint(1, self.n)
        self.at = self.trace[self.k - 1][0]
        self.answer = self.order if self.task_type == "order" else self.at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "order" else "s1"
        return texts.t(
            key, language, base=self.base, modulus=self.modulus, n=self.n, k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, power=power, order=order)
            for index, (power, order) in enumerate(self.trace, 1)
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
