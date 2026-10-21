"""Пространственное мышление: развёртка куба (противоположные грани), игральный
кубик (сумма 7), повороты/отражения фигуры, складывание бумаги."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.spatial_shared.base import _SpatialBase

class DiceReasoningTask(_SpatialBase):
    TASK_TYPE = "dice_reasoning"
    TASK_TYPES = ["opposite", "corner_sum"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        self.augment = augment
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        if self.subtype == "opposite":
            self.v = random.randint(1, 6)
            self.answer = 7 - self.v
        else:
            self.faces = [random.choice(list(pair)) for pair in ((1, 6), (2, 5), (3, 4))]
            random.shuffle(self.faces)
            self.answer = 21 - sum(self.faces)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.subtype == "opposite":
            return ((texts.t('s1', language, v=self.v)))
        fs = ", ".join(map(str, self.faces))
        return ((texts.t('s0', language, fs=fs)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))
