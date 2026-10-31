"""EfficiencyTask — КПД как полезная работа, делённая на затраченную.

Подтипы: сама дробь КПД и полезная работа при известных КПД и затратах.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class EfficiencyTask(BaseMathTask):
    TASK_TYPE = "mechanical_efficiency"
    TASK_TYPES = ["efficiency", "useful"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 8}, 2: {"m": 10}, 3: {"m": 12}, 4: {"m": 12}, 5: {"m": 16},
        6: {"m": 18}, 7: {"m": 20}, 8: {"m": 24}, 9: {"m": 30}, 10: {"m": 36},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["m"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.total = random.randint(2, limit)
        self.useful = random.randint(1, self.total)
        self.efficiency = Fraction(self.useful, self.total)
        self.answer = self.efficiency if self.task_type == "efficiency" else Fraction(self.useful)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "efficiency":
            ask = ((texts.t('s2', language, useful=self.useful, total=self.total)))
        else:
            ask = ((texts.t('s3', language, v0=fmt_fraction(self.efficiency), total=self.total)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, useful=self.useful, total=self.total, v2=fmt_fraction(self.efficiency))))
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
