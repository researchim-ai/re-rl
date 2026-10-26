"""NilIndexTask — индекс нильпотентности в кольце вычетов.

Степени элемента умножаются по модулю степени простого. Индекс — первая нулевая степень.
Показатель модуля растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def nil_power(base: int, modulus: int, steps: int) -> List[Tuple[int, int, int]]:
    power = 1
    index = 0
    last = 0
    trace = []
    for step in range(1, steps + 1):
        power = power * base % modulus
        if power != 0:
            last = power
        elif index == 0:
            index = step
        trace.append((power, index, last))
    if index == 0 or pow(base, index, modulus) != 0:
        raise RuntimeError("index mismatch")
    if index > 1 and pow(base, index - 1, modulus) == 0:
        raise RuntimeError("index mismatch")
    return trace


class NilIndexTask(BaseMathTask):
    TASK_TYPE = "nil_index"
    TASK_TYPES = ["index", "last"]
    PRIMES = (2, 3, 5)

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
        self.n = max(3, int(p["n"]))
        prime = random.choice(self.PRIMES)
        rank = random.randint(1, min(3, self.n - 1))
        self.base = prime ** rank
        self.modulus = prime ** self.n
        self.trace = nil_power(self.base, self.modulus, self.n)
        self.index = self.trace[-1][1]
        self.last = self.trace[-1][2]
        self.answer = self.index if self.task_type == "index" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "index" else "s1"
        return texts.t(key, language, n=self.n, base=self.base, modulus=self.modulus)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, power=power, index=nil_index, last=last)
            for index, (power, nil_index, last) in enumerate(self.trace, 1)
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
