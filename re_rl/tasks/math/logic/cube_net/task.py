"""Пространственное мышление: развёртка куба (противоположные грани), игральный
кубик (сумма 7), повороты/отражения фигуры, складывание бумаги."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.spatial_shared.base import _SpatialBase

class CubeNetTask(_SpatialBase):
    TASK_TYPE = "cube_net"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}
    # позиции креста и пары противоположных граней
    _OPP = {"F": "B", "B": "F", "T": "Bo", "Bo": "T", "L": "R", "R": "L"}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        labels = random.sample("ABCDEFGHIJKLMNPQ", 6)
        self.pos = dict(zip(["T", "L", "F", "R", "B", "Bo"], labels))
        self.query_pos = random.choice(list(self.pos))
        self.query_label = self.pos[self.query_pos]
        self.answer = self.pos[self._OPP[self.query_pos]]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _net(self):
        sp = "  "
        p = self.pos
        return (f"{sp*3}[{p['T']}]\n"
                f"[{p['L']}][{p['F']}][{p['R']}][{p['B']}]\n"
                f"{sp*3}[{p['Bo']}]")

    def _descr(self, language):
        return ((texts.t('s0', language, v0=self._net(), query_label=self.query_label)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, query_label=self.query_label, answer=self.answer))),
        ]
        self.final_answer = self.answer

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer])
