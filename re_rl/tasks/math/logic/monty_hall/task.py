"""Разные логические задачи: расшифровка шифра (Цезарь / подстановка), принцип
Дирихле, парадокс Монти Холла и отношения Аллена между интервалами."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
import string
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.misc_logic_shared.base import _MiscBase

class MontyHallTask(_MiscBase):
    TASK_TYPE = "monty_hall"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        self.n = random.choice([3, 3, 3, 4, 5])
        # ведущий открывает одну козу; переключаемся на одну из оставшихся n-2 дверей
        self.prob = Fraction(self.n - 1, self.n * (self.n - 2)) if self.n > 2 else Fraction(0)
        self.value = float(self.prob)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.n == 3:
            base = ((texts.t('s1', language)))
        else:
            base = ((texts.t('s2', language, n=self.n)))
        q = ((texts.t('s0', language)))
        return base + q

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language, v0=self.prob.numerator, v1=self.prob.denominator))),
        ]
        self.final_answer = f"{self.prob.numerator}/{self.prob.denominator}"

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_value(prediction, self.value, tol=1e-2)
