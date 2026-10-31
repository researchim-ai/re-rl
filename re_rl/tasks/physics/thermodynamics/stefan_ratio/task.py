"""StefanRatioTask — отношение светимостей двух одинаковых площадей.

L2/L1 = (T2/T1)^4. Температура горячего тела — целый множитель температуры первого,
поэтому отношение — целая степень, а обратная задача имеет один положительный ответ.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def luminosity_parts(t1: int, factor: int) -> Tuple[Fraction, int]:
    return Fraction(factor) ** 4, t1 * factor


class StefanRatioTask(BaseMathTask):
    TASK_TYPE = "stefan_ratio"
    TASK_TYPES = ["ratio", "hot"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"t": 4, "k": 2}, 2: {"t": 5, "k": 2}, 3: {"t": 6, "k": 3},
        4: {"t": 6, "k": 3}, 5: {"t": 8, "k": 3}, 6: {"t": 8, "k": 4},
        7: {"t": 10, "k": 4}, 8: {"t": 12, "k": 4}, 9: {"t": 14, "k": 5},
        10: {"t": 16, "k": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.t1 = random.randint(1, int(p["t"]))
        self.factor = random.randint(1, int(p["k"]))
        self.ratio, self.t2 = luminosity_parts(self.t1, self.factor)
        self.answer = self.ratio if self.task_type == "ratio" else Fraction(self.t2)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        law = ((texts.t('s0', language)))
        if self.task_type == "ratio":
            ask = ((texts.t('s1', language, t1=self.t1, t2=self.t2)))
        else:
            ask = ((texts.t('s2', language, t1=self.t1, v1=fmt_fraction(self.ratio))))
        return f"{law} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((f"T2/T1 = {self.factor}, L2/L1 = {fmt_fraction(self.ratio)}, T2 = {self.t2}."))
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
