"""FractionOpsTask — цепочка сложений и умножений дробей.

После каждой операции дробь сокращается. Число операций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[str, int, int]


def apply_fraction_ops(start: int, ops: Sequence[Op]) -> List[Fraction]:
    value = Fraction(start)
    history = []
    for kind, numerator, denominator in ops:
        step = Fraction(numerator, denominator)
        if kind == "add":
            value += step
        else:
            value *= step
        history.append(value)
    return history


class FractionOpsTask(BaseMathTask):
    TASK_TYPE = "fraction_ops"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(1, 4)
        self.ops = [
            (random.choice(("add", "mul")), random.randint(1, 3), random.randint(1, 3))
            for _ in range(self.n)
        ]
        self.history = apply_fraction_ops(self.start, self.ops)
        self.final = self.history[-1]
        self.numer = self.final.numerator
        self.denom = self.final.denominator
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _op(self, language, op: Op) -> str:
        kind, numerator, denominator = op
        key = "s4" if kind == "add" else "s5"
        return texts.t(key, language, num=numerator, den=denominator)

    def _descr(self, language):
        listing = ", ".join(self._op(language, op) for op in self.ops)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, (op, value) in enumerate(zip(self.ops, self.history), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, op=self._op(self.language, op),
                numer=value.numerator, denom=value.denominator,
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
