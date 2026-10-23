"""GaussMulTask — цепочка умножений целых гауссовых чисел.

(a+bi)(c+di) = (ac-bd) + (ad+bc)i. Множители с координатами -1, 0, 1.
Число множителей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Gauss = Tuple[int, int]


def format_gauss(real: int, imag: int) -> str:
    if imag < 0:
        return f"{real}-{abs(imag)}i"
    return f"{real}+{imag}i"


def multiply_gauss(factors: Sequence[Gauss]) -> List[Gauss]:
    real, imag = 1, 0
    trace = []
    for left, right in factors:
        real, imag = real * left - imag * right, real * right + imag * left
        trace.append((real, imag))
    return trace


class GaussMulTask(BaseMathTask):
    TASK_TYPE = "gauss_mul"
    TASK_TYPES = ["real", "imag"]

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
        self.factors = []
        for _ in range(self.n):
            left = random.randint(-1, 1)
            right = random.randint(-1, 1)
            if left == 0 and right == 0:
                left = 1
            self.factors.append((left, right))
        self.trace = multiply_gauss(self.factors)
        self.real, self.imag = self.trace[-1]
        self.answer = self.real if self.task_type == "real" else self.imag
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(format_gauss(left, right) for left, right in self.factors)
        key = "s0" if self.task_type == "real" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, ((left, right), (real, imag)) in enumerate(zip(self.factors, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, factor=format_gauss(left, right),
                real=real, imag=imag,
            ))
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
