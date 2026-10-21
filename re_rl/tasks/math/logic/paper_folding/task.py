"""Пространственное мышление: развёртка куба (противоположные грани), игральный
кубик (сумма 7), повороты/отражения фигуры, складывание бумаги."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.spatial_shared.base import _SpatialBase

class PaperFoldingTask(_SpatialBase):
    TASK_TYPE = "paper_folding"
    TASK_TYPES = ["holes", "layers"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"kmax": 3, "hmax": 2}, 2: {"kmax": 4, "hmax": 2}, 3: {"kmax": 4, "hmax": 3},
        4: {"kmax": 5, "hmax": 3}, 5: {"kmax": 5, "hmax": 4}, 6: {"kmax": 6, "hmax": 4},
        7: {"kmax": 6, "hmax": 5}, 8: {"kmax": 7, "hmax": 5}, 9: {"kmax": 7, "hmax": 6},
        10: {"kmax": 8, "hmax": 6},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self.k = random.randint(1, int(p["kmax"]))
        self.h = random.randint(1, int(p["hmax"]))
        if self.subtype == "layers":
            self.answer = 2 ** self.k
        else:
            self.answer = self.h * (2 ** self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.subtype == "layers":
            return ((texts.t('s1', language, k=self.k)))
        return ((texts.t('s0', language, k=self.k, h=self.h)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s2', self.language, k=self.k, v1=2 ** self.k))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))
