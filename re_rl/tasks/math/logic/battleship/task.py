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

class BattleshipTask(_GridBase):
    TASK_TYPE = "battleship"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "fleet": [2, 1, 1]}, 2: {"n": 5, "fleet": [3, 2, 1]},
        3: {"n": 6, "fleet": [3, 2, 1, 1]}, 4: {"n": 6, "fleet": [3, 2, 2, 1]},
        5: {"n": 6, "fleet": [3, 3, 2, 1]}, 6: {"n": 7, "fleet": [4, 3, 2, 1]},
        7: {"n": 7, "fleet": [4, 3, 2, 2]}, 8: {"n": 8, "fleet": [4, 3, 2, 2, 1]},
        9: {"n": 8, "fleet": [4, 3, 3, 2, 1]}, 10: {"n": 8, "fleet": [5, 4, 3, 2, 1]},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.fleet = list(p["fleet"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        n = self.n
        for _ in range(500):
            grid = [[0] * n for _ in range(n)]
            if self._place_all(grid, sorted(self.fleet, reverse=True)):
                self.sol = grid
                self.row_counts = [sum(grid[i]) for i in range(n)]
                self.col_counts = [sum(grid[i][j] for i in range(n)) for j in range(n)]
                return
        self.sol = [[0] * n for _ in range(n)]
        self.row_counts = [0] * n
        self.col_counts = [0] * n

    def _place_all(self, grid, ships):
        if not ships:
            return True
        size = ships[0]
        n = self.n
        placements = []
        for r in range(n):
            for c in range(n):
                for dr, dc in ((0, 1), (1, 0)):
                    cells = [(r + dr * k, c + dc * k) for k in range(size)]
                    if all(0 <= x < n and 0 <= y < n for x, y in cells) and self._can_place(grid, cells):
                        placements.append(cells)
        random.shuffle(placements)
        for cells in placements:
            for x, y in cells:
                grid[x][y] = 1
            if self._place_all(grid, ships[1:]):
                return True
            for x, y in cells:
                grid[x][y] = 0
        return False

    def _can_place(self, grid, cells):
        n = self.n
        for x, y in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 1:
                        return False
        return True

    def _descr(self, language):
        fleet = ", ".join(map(str, sorted(self.fleet, reverse=True)))
        rc = ", ".join(map(str, self.row_counts))
        cc = ", ".join(map(str, self.col_counts))
        return ((texts.t('s0', language, n=self.n, n_2=self.n, fleet=fleet, rc=rc, cc=cc, v5=self.n * self.n)))

    def solve(self):
        flat = " ".join(str(self.sol[i][j]) for i in range(self.n) for j in range(self.n))
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, flat=flat))),
        ]
        self.final_answer = flat

    def _valid_board(self, grid) -> bool:
        n = self.n
        if [sum(grid[i]) for i in range(n)] != self.row_counts:
            return False
        if [sum(grid[i][j] for i in range(n)) for j in range(n)] != self.col_counts:
            return False
        # компоненты (орто) — прямые отрезки; длины = флот; без касаний по диагонали
        seen = [[False] * n for _ in range(n)]
        comps = []
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1 and not seen[i][j]:
                    cells = []
                    q = deque([(i, j)]); seen[i][j] = True
                    while q:
                        x, y = q.popleft(); cells.append((x, y))
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 1 and not seen[nx][ny]:
                                seen[nx][ny] = True; q.append((nx, ny))
                    comps.append(cells)
        lengths = []
        for cells in comps:
            rs = {x for x, _ in cells}
            cs = {y for _, y in cells}
            if len(rs) != 1 and len(cs) != 1:  # не прямая линия
                return False
            lengths.append(len(cells))
        if sorted(lengths, reverse=True) != sorted(self.fleet, reverse=True):
            return False
        # непересечение: соседи по диагонали должны быть той же компоненты (значит — не касаются)
        comp_id = {}
        for idx, cells in enumerate(comps):
            for cell in cells:
                comp_id[cell] = idx
        for (x, y), idx in comp_id.items():
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in comp_id and comp_id[nb] != idx:
                        return False
        return True

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        n = self.n
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < n * n:
            return 0.0
        flat = ints[-n * n:]
        grid = [flat[i * n:(i + 1) * n] for i in range(n)]
        return 1.0 if self._valid_board(grid) else 0.0
