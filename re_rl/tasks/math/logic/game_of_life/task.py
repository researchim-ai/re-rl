"""Симуляция автоматов и клеточных систем.

- DFASimulationTask: принимает ли ДКА заданную строку;
- TuringMachineTask: число единиц на ленте после N шагов машины Тьюринга;
- GameOfLifeTask: состояние поля «Жизни» после k шагов;
- ElementaryCATask: строка одномерного клеточного автомата после k шагов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.automata_sim_shared.base import _SimBase

class GameOfLifeTask(_SimBase):
    TASK_TYPE = texts.literal('literals.s3')
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 3, "c": 3, "k": 1}, 2: {"r": 3, "c": 3, "k": 1}, 3: {"r": 3, "c": 4, "k": 1},
        4: {"r": 4, "c": 4, "k": 1}, 5: {"r": 4, "c": 4, "k": 2}, 6: {"r": 4, "c": 5, "k": 2},
        7: {"r": 5, "c": 5, "k": 2}, 8: {"r": 5, "c": 5, "k": 2}, 9: {"r": 5, "c": 6, "k": 3},
        10: {"r": 6, "c": 6, "k": 3},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c, self.k = int(p["r"]), int(p["c"]), int(p["k"])
        self.augment = augment
        self.grid0 = [[random.randint(0, 1) for _ in range(self.c)] for _ in range(self.r)]
        self.grid = [row[:] for row in self.grid0]
        for _ in range(self.k):
            self.grid = self._step(self.grid)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _step(self, g):
        r, c = self.r, self.c
        new = [[0] * c for _ in range(r)]
        for i in range(r):
            for j in range(c):
                n = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < r and 0 <= nj < c:
                            n += g[ni][nj]
                new[i][j] = 1 if (g[i][j] and n in (2, 3)) or (not g[i][j] and n == 3) else 0
        return new

    @staticmethod
    def _grid_str(g):
        return "\n".join(" ".join(map(str, row)) for row in g)

    def _descr(self, language):
        return ((texts.t('s0', language, r=self.r, c=self.c, v2=self._grid_str(self.grid0), k=self.k, v4=self.r * self.c)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, v0=self._grid_str(self.grid)))),
        ]
        self.final_answer = " ".join(str(self.grid[i][j]) for i in range(self.r) for j in range(self.c))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        flat = [self.grid[i][j] for i in range(self.r) for j in range(self.c)]
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < len(flat):
            return 0.0
        return 1.0 if ints[-len(flat):] == flat else 0.0
