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

class StarBattleTask(_GridBase):
    TASK_TYPE = "star_battle"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 7},
    }
    _LET = "ABCDEFGHIJ"

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _gen_stars(self):
        n = self.n
        for _ in range(2000):
            cols = list(range(n))
            random.shuffle(cols)
            ok = all(abs(cols[r] - cols[r + 1]) >= 2 for r in range(n - 1))
            if ok:
                return [(r, cols[r]) for r in range(n)]
        from re_rl.tasks.math.logic.board_search_traces import star_battle
        result = star_battle([[r]*n for r in range(n)])
        if result is None: raise RuntimeError('generation_failed')
        return result

    def _partition(self, stars):
        n = self.n
        region = [[-1] * n for _ in range(n)]
        q = deque()
        for idx, (r, c) in enumerate(stars):
            region[r][c] = idx
            q.append((r, c))
        while q:
            r, c = q.popleft()
            neigh = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            random.shuffle(neigh)
            for nr, nc in neigh:
                if 0 <= nr < n and 0 <= nc < n and region[nr][nc] == -1:
                    region[nr][nc] = region[r][c]
                    q.append((nr, nc))
        return region

    def _build(self):
        self.stars = self._gen_stars()
        self.region = self._partition(self.stars)

    def _descr(self, language):
        rows = "\n".join(" ".join(self._LET[self.region[i][j]] for j in range(self.n))
                         for i in range(self.n))
        return ((texts.t('s0', language, n=self.n, n_2=self.n, n_3=self.n, rows=rows)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        coords = ", ".join(f"({r+1}, {c+1})" for (r, c) in sorted(self.stars))
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, coords=coords))),
        ]
        self.final_answer = coords

    def _valid_stars(self, stars) -> bool:
        n = self.n
        if len(stars) != n:
            return False
        if any(not (0 <= r < n and 0 <= c < n) for (r, c) in stars):
            return False
        if len({r for r, _ in stars}) != n or len({c for _, c in stars}) != n:
            return False
        if len({self.region[r][c] for (r, c) in stars}) != n:
            return False
        star_list = list(stars)
        for a in range(len(star_list)):
            for b in range(a + 1, len(star_list)):
                (r1, c1), (r2, c2) = star_list[a], star_list[b]
                if max(abs(r1 - r2), abs(c1 - c2)) <= 1:
                    return False
        return True

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        from re_rl.tasks.math.logic.grids2_shared.coordinates import parse_coordinates
        stars = parse_coordinates(prediction)
        return 1.0 if stars is not None and self._valid_stars(stars) else 0.0
