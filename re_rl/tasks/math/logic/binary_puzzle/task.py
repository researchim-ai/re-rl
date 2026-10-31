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

class BinaryPuzzleTask(_GridBase):
    TASK_TYPE = "binary_puzzle"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "blanks": 6}, 2: {"n": 4, "blanks": 8}, 3: {"n": 4, "blanks": 9},
        4: {"n": 6, "blanks": 12}, 5: {"n": 6, "blanks": 15}, 6: {"n": 6, "blanks": 18},
        7: {"n": 6, "blanks": 20}, 8: {"n": 8, "blanks": 26}, 9: {"n": 8, "blanks": 32},
        10: {"n": 8, "blanks": 38},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.blanks = int(p["blanks"])
        self.augment = augment
        self.sol = self._generate_board()
        self._make_puzzle()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _generate_board(self):
        n = self.n
        for _ in range(500):
            grid = [[-1] * n for _ in range(n)]
            if self._fill(grid, 0):
                cols = [tuple(grid[i][j] for i in range(n)) for j in range(n)]
                rows = [tuple(row) for row in grid]
                if len(set(rows)) == n and len(set(cols)) == n:
                    return grid
        raise RuntimeError('generation_failed')

    def _fill(self, grid, pos):
        n = self.n
        if pos == n * n:
            return True
        r, c = divmod(pos, n)
        vals = [0, 1]
        random.shuffle(vals)
        for v in vals:
            grid[r][c] = v
            if self._ok(grid, r, c):
                if self._fill(grid, pos + 1):
                    return True
        grid[r][c] = -1
        return False

    def _ok(self, grid, r, c):
        n = self.n
        row = grid[r]
        col = [grid[i][c] for i in range(n)]
        # не более n/2 единиц/нулей
        for line, idx in ((row, c), (col, r)):
            filled = [x for x in line if x != -1]
            if filled.count(0) > n // 2 or filled.count(1) > n // 2:
                return False
        # нет трёх подряд
        if c >= 2 and grid[r][c] == grid[r][c-1] == grid[r][c-2] != -1:
            return False
        if r >= 2 and grid[r][c] == grid[r-1][c] == grid[r-2][c] != -1:
            return False
        if -1 not in row:
            if any(other != r and grid[other] == row for other in range(n)):
                return False
        if -1 not in col:
            if any(other != c and [grid[i][other] for i in range(n)] == col for other in range(n)):
                return False
        return True

    def _make_puzzle(self):
        n = self.n
        cells = [(i, j) for i in range(n) for j in range(n)]
        random.shuffle(cells)
        self.hidden = set(cells[:self.blanks])
        self.given = {(i, j): self.sol[i][j] for (i, j) in cells[self.blanks:]}

    def _grid_str(self):
        rows = []
        for i in range(self.n):
            rows.append(" ".join(str(self.sol[i][j]) if (i, j) not in self.hidden else "?"
                                  for j in range(self.n)))
        return "\n".join(rows)

    def _descr(self, language):
        return ((texts.t('s0', language, n=self.n, n_2=self.n, v2=self.n * self.n, v3=self._grid_str())))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        flat = " ".join(str(self.sol[i][j]) for i in range(self.n) for j in range(self.n))
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, flat=flat))),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        n = self.n
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < n * n:
            return 0.0
        flat = ints[-n * n:]
        grid = [flat[i * n:(i + 1) * n] for i in range(n)]
        for (i, j), v in self.given.items():
            if grid[i][j] != v:
                return 0.0
        for i in range(n):
            if grid[i].count(1) != n // 2:
                return 0.0
            col = [grid[k][i] for k in range(n)]
            if col.count(1) != n // 2:
                return 0.0
            for k in range(n - 2):
                if grid[i][k] == grid[i][k+1] == grid[i][k+2]:
                    return 0.0
                if col[k] == col[k+1] == col[k+2]:
                    return 0.0
        rows = [tuple(r) for r in grid]
        cols = [tuple(grid[i][j] for i in range(n)) for j in range(n)]
        if len(set(rows)) != n or len(set(cols)) != n:
            return 0.0
        return 1.0
