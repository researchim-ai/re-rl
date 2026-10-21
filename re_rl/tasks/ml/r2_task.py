"""R2Task — коэффициент детерминации.

R^2 = 1 - SS_res / SS_tot.
SS_tot — сумма квадратов отклонений истины от её среднего, SS_res — от прогноза.
Если все истинные значения равны, последнее сдвигается, чтобы знаменатель не обнулился.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def r2_parts(truth: List[int], pred: List[int]) -> Tuple[Fraction, Fraction, Fraction]:
    mean = Fraction(sum(truth), len(truth))
    ss_tot = sum((Fraction(value) - mean) ** 2 for value in truth)
    ss_res = sum((Fraction(hat) - Fraction(value)) ** 2 for hat, value in zip(pred, truth))
    return 1 - ss_res / ss_tot, ss_tot, ss_res


class R2Task(BaseMathTask):
    TASK_TYPE = "r2_score"
    TASK_TYPES = ["r2", "ss_tot"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 3}, 2: {"n": 3, "mag": 4}, 3: {"n": 3, "mag": 5},
        4: {"n": 4, "mag": 5}, 5: {"n": 4, "mag": 6}, 6: {"n": 4, "mag": 6},
        7: {"n": 5, "mag": 7}, 8: {"n": 5, "mag": 8}, 9: {"n": 6, "mag": 8},
        10: {"n": 6, "mag": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.truth = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        if len(set(self.truth)) == 1:
            self.truth[-1] += 1
        self.pred = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.r2, self.ss_tot, self.ss_res = r2_parts(self.truth, self.pred)
        self.answer = self.r2 if self.task_type == "r2" else self.ss_tot
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        truth = ", ".join(map(str, self.truth))
        pred = ", ".join(map(str, self.pred))
        rule = ((f"Истинные значения: {truth}. Прогнозы: {pred}. "
                 f"SS_tot — сумма квадратов отклонений истины от её среднего. "
                 f"SS_res — сумма квадратов разностей прогноза и истины. "
                 f"R^2 = 1 - SS_res / SS_tot. Ответ — целое или несократимая дробь.") if ru else
                (f"True values: {truth}. Predictions: {pred}. "
                 f"SS_tot is the sum of squared deviations of the truth from its mean. "
                 f"SS_res is the sum of squared prediction errors. "
                 f"R^2 = 1 - SS_res / SS_tot. Answer with an integer or a reduced fraction."))
        ask = (("Найдите R^2." if ru else "Find R^2.") if self.task_type == "r2" else
               ("Найдите SS_tot." if ru else "Find SS_tot."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"SS_tot = {fmt_fraction(self.ss_tot)}, SS_res = {fmt_fraction(self.ss_res)}, "
                 f"R^2 = {fmt_fraction(self.r2)}.") if ru else
                (f"SS_tot = {fmt_fraction(self.ss_tot)}, SS_res = {fmt_fraction(self.ss_res)}, "
                 f"R^2 = {fmt_fraction(self.r2)}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
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
