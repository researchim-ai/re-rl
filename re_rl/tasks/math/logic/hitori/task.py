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
from re_rl.tasks.math.logic.grids2_shared.base import _GridBase

class HitoriTask(_GridBase):
    TASK_TYPE = "hitori"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 7},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pick_shaded(self):
        n = self.n
        for _ in range(300):
            shaded = set()
            for i in range(n):
                for j in range(n):
                    if random.random() < 0.18:
                        # не соседняя с уже затенёнными
                        if all((i + di, j + dj) not in shaded for di, dj in
                               ((1, 0), (-1, 0), (0, 1), (0, -1))):
                            shaded.add((i, j))
            if shaded and self._complement_connected(shaded) and self._each_row_col_has_free(shaded):
                return shaded
        # запасной вариант: одна клетка (всегда корректно и не вырождено)
        return {(random.randrange(n), random.randrange(n))}

    def _each_row_col_has_free(self, shaded):
        n = self.n
        for i in range(n):
            if all((i, j) in shaded for j in range(n)):
                return False
        for j in range(n):
            if all((i, j) in shaded for i in range(n)):
                return False
        return True

    def _complement_connected(self, shaded):
        n = self.n
        free = [(i, j) for i in range(n) for j in range(n) if (i, j) not in shaded]
        if not free:
            return False
        seen = {free[0]}
        q = deque([free[0]])
        while q:
            i, j = q.popleft()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (i + di, j + dj)
                if 0 <= nb[0] < n and 0 <= nb[1] < n and nb not in shaded and nb not in seen:
                    seen.add(nb); q.append(nb)
        return len(seen) == len(free)

    def _build(self):
        n = self.n
        self.shaded = self._pick_shaded()
        base = [[(i + j) % n + 1 for j in range(n)] for i in range(n)]  # латинский квадрат
        grid = [row[:] for row in base]
        for (i, j) in self.shaded:
            free_cols = [c for c in range(n) if (i, c) not in self.shaded and c != j]
            if free_cols:
                c2 = random.choice(free_cols)
                grid[i][j] = base[i][c2]  # дубликат в строке -> клетку нужно затенить
        self.grid = grid

    def _descr(self, language):
        rows = "\n".join(" ".join(str(self.grid[i][j]) for j in range(self.n)) for i in range(self.n))
        return ((texts.t('s0', language, n=self.n, n_2=self.n, rows=rows)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        coords = ", ".join(f"({i+1}, {j+1})" for (i, j) in sorted(self.shaded))
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, coords=coords))),
        ]
        self.final_answer = coords if coords else ((texts.t('s3', self.language)))

    def _valid_shading(self, shaded) -> bool:
        n = self.n
        if any(not (0 <= i < n and 0 <= j < n) for (i, j) in shaded):
            return False
        for (i, j) in shaded:  # не соседние
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (i + di, j + dj) in shaded:
                    return False
        for i in range(n):  # нет дубликатов среди незатенённых
            vals = [self.grid[i][j] for j in range(n) if (i, j) not in shaded]
            if len(vals) != len(set(vals)):
                return False
        for j in range(n):
            vals = [self.grid[i][j] for i in range(n) if (i, j) not in shaded]
            if len(vals) != len(set(vals)):
                return False
        return self._complement_connected(shaded)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        from re_rl.tasks.math.logic.grids2_shared.coordinates import parse_coordinates
        shaded = parse_coordinates(prediction,empty_labels=(texts.t('s3',self.language),))
        return 1.0 if shaded is not None and self._valid_shading(shaded) else 0.0
