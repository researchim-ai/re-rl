"""ThueCountTask — последовательность Туэ–Морса.

Бит номера k — остаток числа единиц в двоичной записи k. Нумерация с нуля.
Длина растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def thue_bit(index: int) -> int:
    ones = 0
    while index:
        ones += index & 1
        index >>= 1
    return ones % 2


def thue_trace(length: int) -> List[Tuple[int, int]]:
    ones = 0
    trace = []
    for index in range(length):
        bit = thue_bit(index)
        ones += bit
        trace.append((bit, ones))
    return trace


class ThueCountTask(BaseMathTask):
    TASK_TYPE = "thue_count"
    TASK_TYPES = ["ones", "bit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = thue_trace(self.n)
        self.k = random.randint(0, self.n - 1)
        self.bit = self.trace[self.k][0]
        self.ones = self.trace[-1][1]
        self.answer = self.ones if self.task_type == "ones" else self.bit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "ones" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, ones=ones)
            for index, (bit, ones) in enumerate(self.trace)
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
