"""EligibilityTraceTask — накапливающийся след затухания.

Сначала каждая координата умножается на γλ, затем к посещённой прибавляется 1.
Номера координат с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

_FACTORS = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(3, 4)]


def accumulating_trace(trace: List[int], gamma: Fraction, lam: Fraction, visited: int) -> List[Fraction]:
    factor = gamma * lam
    updated = [factor * value for value in trace]
    updated[visited] += 1
    return updated


class EligibilityTraceTask(BaseMathTask):
    TASK_TYPE = "eligibility_trace"
    TASK_TYPES = ["visited", "other"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 2, "mag": 2}, 2: {"d": 2, "mag": 3}, 3: {"d": 3, "mag": 3},
        4: {"d": 3, "mag": 4}, 5: {"d": 3, "mag": 5}, 6: {"d": 4, "mag": 5},
        7: {"d": 4, "mag": 6}, 8: {"d": 4, "mag": 7}, 9: {"d": 5, "mag": 8},
        10: {"d": 5, "mag": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.dim = int(p["d"])
        self.mag = int(p["mag"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.trace = [random.randint(0, self.mag) for _ in range(self.dim)]
        span = _FACTORS[:1 + min(3, difficulty // 3)]
        self.gamma = random.choice(span)
        self.lam = random.choice(span)
        self.visited = random.randrange(self.dim)
        self.updated = accumulating_trace(self.trace, self.gamma, self.lam, self.visited)
        if self.task_type == "visited":
            self.index = self.visited
        else:
            choices = [i for i in range(self.dim) if i != self.visited]
            self.index = random.choice(choices)
        self.answer = self.updated[self.index]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(map(str, self.trace))
        rule = ((texts.t('s0', language, v0=fmt_fraction(self.gamma), v1=fmt_fraction(self.lam))))
        data = ((texts.t('s1', language, shown=shown, v1=self.visited + 1)))
        ask = ((texts.t('s2', language, v0=self.index + 1)))
        return f"{rule} {data} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s3', self.language, v0=self.index + 1, shown=shown)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
