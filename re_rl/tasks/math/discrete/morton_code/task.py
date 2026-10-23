"""MortonCodeTask — код Мортона, чередование битов двух чисел.

От старшего бита к младшему сначала берётся бит y, затем бит x.
Число битов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def morton_trace(x: int, y: int, bits: int) -> List[int]:
    code = 0
    trace = []
    for index in range(bits - 1, -1, -1):
        code = (code << 2) | (((y >> index) & 1) << 1) | ((x >> index) & 1)
        trace.append(code)
    return trace


class MortonCodeTask(BaseMathTask):
    TASK_TYPE = "morton_code"
    TASK_TYPES = ["code", "bit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        span = 1 << self.n
        self.x = random.randint(0, span - 1)
        self.y = random.randint(0, span - 1)
        self.trace = morton_trace(self.x, self.y, self.n)
        self.code = self.trace[-1]
        self.k = random.randint(1, self.n)
        self.bit = (self.x >> (self.k - 1)) & 1
        self.answer = self.code if self.task_type == "code" else self.bit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "code" else "s1"
        return texts.t(key, language, x=self.x, y=self.y, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code)
            for index, code in enumerate(self.trace, 1)
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
