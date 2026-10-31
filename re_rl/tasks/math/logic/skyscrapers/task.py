"""SkyscrapersTask — головоломка «Небоскрёбы» 4×4.

В сетке высоты 1..N, в каждой строке и столбце — все высоты по разу (латинский
квадрат). Числа у краёв показывают, сколько небоскрёбов видно с этой стороны
(более высокие закрывают более низкие). Единственность решения проверяется
перебором всех латинских квадратов порядка N.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _visible(seq) -> int:
    best, cnt = 0, 0
    for h in seq:
        if h > best:
            best = h
            cnt += 1
    return cnt


class SkyscrapersTask(BaseMathTask):
    TASK_TYPE = "skyscrapers"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {"n": 4} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        self.n = 4
        self.augment = augment
        self.squares = U.all_latin_squares(self.n)
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _clues_for(self, grid):
        n = self.n
        top = [_visible([grid[r][c] for r in range(n)]) for c in range(n)]
        bottom = [_visible([grid[r][c] for r in range(n - 1, -1, -1)]) for c in range(n)]
        left = [_visible(grid[r]) for r in range(n)]
        right = [_visible(grid[r][::-1]) for r in range(n)]
        return {"top": top, "bottom": bottom, "left": left, "right": right}

    def _consistent(self, grid, clues) -> bool:
        c2 = self._clues_for(grid)
        return all(c2[side] == clues[side] for side in clues)

    def _build(self):
        # Даём полный набор краевых подсказок; засчитывается любое согласованное
        # заполнение (обычно оно единственно).
        self.solution = random.choice(self.squares)
        self.clues = self._clues_for(self.solution)

    def _make_description(self, language: str) -> str:
        n = self.n
        top = "   " + " ".join(str(x) for x in self.clues["top"])
        rows = []
        for r in range(n):
            rows.append(f"{self.clues['left'][r]}  " + " ".join("?" for _ in range(n))
                        + f"  {self.clues['right'][r]}")
        bottom = "   " + " ".join(str(x) for x in self.clues["bottom"])
        grid = "\n".join([top] + rows + [bottom])
        return ((texts.t('s0', language, n=n, n_2=n, n_3=n, v3=n * n, grid=grid)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        flat = [self.solution[r][c] for r in range(self.n) for c in range(self.n)]
        nums = " ".join(str(x) for x in flat)
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, nums=nums))),
        ]
        self.final_answer = nums

    def _check_grid(self, flat: List[int]) -> bool:
        n = self.n
        if len(flat) != n * n:
            return False
        grid = [flat[r * n:(r + 1) * n] for r in range(n)]
        for i in range(n):
            if sorted(grid[i]) != list(range(1, n + 1)):
                return False
            if sorted(grid[r][i] for r in range(n)) != list(range(1, n + 1)):
                return False
        return self._consistent(tuple(tuple(row) for row in grid), self.clues)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) < self.n * self.n:
            return 0.0
        return 1.0 if self._check_grid(ints[-self.n * self.n:]) else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
