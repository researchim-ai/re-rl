"""PickTheoremTask — формула Пика.

Площадь = I + B/2 - 1, где I — внутренние узлы решётки, B — узлы на границе.
Ответ — точная дробь.

Подтипы: площадь и число внутренних узлов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def pick_area(interior: int, boundary: int) -> Fraction:
    return Fraction(interior) + Fraction(boundary, 2) - 1


class PickTheoremTask(BaseMathTask):
    TASK_TYPE = "pick_theorem"
    TASK_TYPES = ["area", "interior"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"i": 4, "b": 8}, 2: {"i": 6, "b": 10}, 3: {"i": 8, "b": 12},
        4: {"i": 10, "b": 12}, 5: {"i": 12, "b": 16}, 6: {"i": 14, "b": 16},
        7: {"i": 16, "b": 20}, 8: {"i": 20, "b": 24}, 9: {"i": 24, "b": 28},
        10: {"i": 30, "b": 36},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.interior = random.randint(0, int(p["i"]))
        self.boundary = random.randint(3, int(p["b"]))
        self.area = pick_area(self.interior, self.boundary)
        if self.area <= 0:
            self.interior += 1
            self.area = pick_area(self.interior, self.boundary)
        self.answer = self.area if self.task_type == "area" else Fraction(self.interior)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "area":
            ask = ((texts.t('s2', language, interior=self.interior, boundary=self.boundary)))
        else:
            ask = ((texts.t('s3', language, v0=fmt_fraction(self.area), boundary=self.boundary)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, interior=self.interior, boundary=self.boundary, v2=fmt_fraction(self.area))))
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
