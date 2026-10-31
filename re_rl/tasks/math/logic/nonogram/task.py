"""Сеточные головоломки с проверкой по правилам (засчитывается любое корректное
решение): нонограмма, бинарная головоломка (такузу), хитори, «Битва звёзд»
(Star Battle) и «Морской бой» (Battleship solitaire).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.grids2_shared.base import _GridBase, _runs

class NonogramTask(_GridBase):
    TASK_TYPE = "nonogram"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 3, "c": 3}, 2: {"r": 4, "c": 4}, 3: {"r": 5, "c": 5}, 4: {"r": 5, "c": 5},
        5: {"r": 5, "c": 6}, 6: {"r": 6, "c": 6}, 7: {"r": 6, "c": 7}, 8: {"r": 7, "c": 7},
        9: {"r": 7, "c": 8}, 10: {"r": 8, "c": 8},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c = int(p["r"]), int(p["c"])
        self.augment = augment
        self.sol = [[1 if random.random() < 0.55 else 0 for _ in range(self.c)]
                    for _ in range(self.r)]
        self.row_clues = [_runs(self.sol[i]) for i in range(self.r)]
        self.col_clues = [_runs([self.sol[i][j] for i in range(self.r)]) for j in range(self.c)]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _clue_str(self, clue):
        return " ".join(map(str, clue)) if clue else "0"

    def _descr(self, language):
        rows = ("\n".join(texts.t('s0', language, v0=i + 1, v1=self._clue_str(self.row_clues[i])) for i in range(self.r)))
        cols = ("\n".join(texts.t('s1', language, v0=j + 1, v1=self._clue_str(self.col_clues[j])) for j in range(self.c)))
        return ((texts.t('s2', language, r=self.r, c=self.c, rows=rows, cols=cols, v4=self.r * self.c)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        flat = " ".join(str(self.sol[i][j]) for i in range(self.r) for j in range(self.c))
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language, flat=flat))),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < self.r * self.c:
            return 0.0
        flat = ints[-self.r * self.c:]
        grid = [flat[i * self.c:(i + 1) * self.c] for i in range(self.r)]
        for i in range(self.r):
            if _runs(grid[i]) != self.row_clues[i]:
                return 0.0
        for j in range(self.c):
            if _runs([grid[i][j] for i in range(self.r)]) != self.col_clues[j]:
                return 0.0
        return 1.0
