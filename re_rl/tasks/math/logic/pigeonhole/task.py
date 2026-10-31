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

class PigeonholeTask(_MiscBase):
    TASK_TYPE = "pigeonhole"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"cmax": 3, "kmax": 2}, 2: {"cmax": 4, "kmax": 2}, 3: {"cmax": 4, "kmax": 3},
        4: {"cmax": 5, "kmax": 3}, 5: {"cmax": 6, "kmax": 3}, 6: {"cmax": 6, "kmax": 4},
        7: {"cmax": 7, "kmax": 4}, 8: {"cmax": 8, "kmax": 5}, 9: {"cmax": 9, "kmax": 5},
        10: {"cmax": 10, "kmax": 6},
    }
    _ITEMS = {"ru": [texts.literal('literals.s3'), texts.literal('literals.s4'), texts.literal('literals.s5'), texts.literal('literals.s6'), texts.literal('literals.s7')],
              "en": ["socks", "gloves", "balls", "pencils", "candies"]}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.colors = random.randint(2, int(p["cmax"]))
        self.k = random.randint(2, int(p["kmax"]))
        self.augment = augment
        self.item = random.choice(self._ITEMS[(texts.t('s2', language))])
        self.answer = self.colors * (self.k - 1) + 1
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, item=self.item, colors=self.colors, k=self.k)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, v0=self.k - 1, colors=self.colors, v2=self.k - 1, k=self.k))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))
