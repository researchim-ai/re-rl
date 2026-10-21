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

class AllenRelationsTask(_MiscBase):
    TASK_TYPE = "allen_relations"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}
    _SYN = {
        "before": ["before", texts.literal('literals.s3'), texts.literal('literals.s4')],
        "after": ["after", texts.literal('literals.s5'), texts.literal('literals.s6')],
        "meets": ["meets", texts.literal('literals.s7')],
        "met-by": ["met by", "met-by", texts.literal('literals.s8')],
        "overlaps": ["overlaps", texts.literal('literals.s9')],
        "overlapped-by": ["overlapped by", "overlapped-by", texts.literal('literals.s10')],
        "starts": ["starts", texts.literal('literals.s11')],
        "started-by": ["started by", "started-by", texts.literal('literals.s12')],
        "during": ["during", texts.literal('literals.s13'), texts.literal('literals.s14')],
        "contains": ["contains", texts.literal('literals.s15')],
        "finishes": ["finishes", texts.literal('literals.s16')],
        "finished-by": ["finished by", "finished-by", texts.literal('literals.s17')],
        "equal": ["equal", texts.literal('literals.s18'), texts.literal('literals.s19')],
    }
    _NAMES = list(_SYN.keys())

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _relation(self, a1, a2, b1, b2):
        if a2 < b1:
            return "before"
        if a1 > b2:
            return "after"
        if a2 == b1:
            return "meets"
        if a1 == b2:
            return "met-by"
        if a1 == b1 and a2 == b2:
            return "equal"
        if a1 == b1:
            return "starts" if a2 < b2 else "started-by"
        if a2 == b2:
            return "finishes" if a1 > b1 else "finished-by"
        if a1 < b1 and b2 < a2:
            return "contains"
        if b1 < a1 and a2 < b2:
            return "during"
        if a1 < b1 < a2 < b2:
            return "overlaps"
        if b1 < a1 < b2 < a2:
            return "overlapped-by"
        return "equal"

    def _build(self):
        for _ in range(200):
            a1 = random.randint(0, 8)
            a2 = a1 + random.randint(1, 6)
            b1 = random.randint(0, 8)
            b2 = b1 + random.randint(1, 6)
            self.A = (a1, a2)
            self.B = (b1, b2)
            self.rel = self._relation(a1, a2, b1, b2)
            if self.rel:
                return

    def _descr(self, language):
        names = ", ".join(self._NAMES)
        return ((texts.t('s0', language, v0=self.A[0], v1=self.A[1], v2=self.B[0], v3=self.B[1], names=names)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, rel=self.rel))),
        ]
        self.final_answer = self.rel

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        # выбираем отношение с самым длинным совпавшим синонимом (устраняем «before» ⊂ «...»)
        best, best_len = None, 0
        for rel, syns in self._SYN.items():
            for s in syns:
                if U.verify_label(prediction, [s]) == 1.0 and len(s) > best_len:
                    best, best_len = rel, len(s)
        return 1.0 if best == self.rel else 0.0
