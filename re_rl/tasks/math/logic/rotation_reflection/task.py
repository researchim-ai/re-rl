"""Пространственное мышление: развёртка куба (противоположные грани), игральный
кубик (сумма 7), повороты/отражения фигуры, складывание бумаги."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.spatial_shared.base import _SpatialBase

class RotationReflectionTask(_SpatialBase):
    TASK_TYPE = "rotation_reflection"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 2, "c": 2}, 2: {"r": 2, "c": 3}, 3: {"r": 3, "c": 3}, 4: {"r": 3, "c": 3},
        5: {"r": 3, "c": 4}, 6: {"r": 4, "c": 4}, 7: {"r": 4, "c": 4}, 8: {"r": 4, "c": 5},
        9: {"r": 5, "c": 5}, 10: {"r": 5, "c": 6},
    }
    _OPS = ["rot90cw", "rot90ccw", "rot180", "flip_h", "flip_v", "transpose"]

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c = int(p["r"]), int(p["c"])
        self.augment = augment
        self.op = random.choice(self._OPS)
        self.grid = [[random.randint(0, 1) for _ in range(self.c)] for _ in range(self.r)]
        self.result = self._apply(self.grid, self.op)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @staticmethod
    def _apply(g, op):
        if op == "rot90cw":
            return [list(row) for row in zip(*g[::-1])]
        if op == "rot90ccw":
            return [list(row) for row in zip(*g)][::-1]
        if op == "rot180":
            return [row[::-1] for row in g[::-1]]
        if op == "flip_h":
            return [row[::-1] for row in g]
        if op == "flip_v":
            return g[::-1]
        return [list(row) for row in zip(*g)]  # transpose

    def _op_text(self, ru):
        return {
            "rot90cw": ((texts.t('s3', self.language))),
            "rot90ccw": ((texts.t('s4', self.language))),
            "rot180": ((texts.t('s5', self.language))),
            "flip_h": ((texts.t('s6', self.language))),
            "flip_v": ((texts.t('s7', self.language))),
            "transpose": ((texts.t('s8', self.language))),
        }[self.op]

    @staticmethod
    def _grid_str(g):
        return "\n".join(" ".join(map(str, row)) for row in g)

    def _descr(self, language):
        rr, cc = len(self.result), len(self.result[0])
        return ((texts.t('s0', language, r=self.r, c=self.c, v2=self._grid_str(self.grid), v3=self._op_text(True), rr=rr, cc=cc, v6=rr * cc)))

    def solve(self):
        flat = " ".join(str(x) for row in self.result for x in row)
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, flat=flat))),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        flat = [x for row in self.result for x in row]
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < len(flat):
            return 0.0
        return 1.0 if ints[-len(flat):] == flat else 0.0
