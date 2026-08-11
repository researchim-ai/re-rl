"""SkyscrapersTask — головоломка «Небоскрёбы» 4×4.

В сетке высоты 1..N, в каждой строке и столбце — все высоты по разу (латинский
квадрат). Числа у краёв показывают, сколько небоскрёбов видно с этой стороны
(более высокие закрывают более низкие). Единственность решения проверяется
перебором всех латинских квадратов порядка N.
"""

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
        ru = language == "ru"
        n = self.n
        top = "   " + " ".join(str(x) for x in self.clues["top"])
        rows = []
        for r in range(n):
            rows.append(f"{self.clues['left'][r]}  " + " ".join("?" for _ in range(n))
                        + f"  {self.clues['right'][r]}")
        bottom = "   " + " ".join(str(x) for x in self.clues["bottom"])
        grid = "\n".join([top] + rows + [bottom])
        return ((f"«Небоскрёбы» {n}×{n}. В каждой строке и столбце высоты 1..{n} без повторений. "
                 f"Число у края — сколько небоскрёбов видно с этой стороны (высокие закрывают низкие). "
                 f"Заполните сетку и выпишите все {n * n} высот по строкам сверху вниз.\n{grid}") if ru else
                (f"{n}×{n} Skyscrapers. Each row and column contains heights 1..{n} once. A border "
                 f"number tells how many skyscrapers are visible from that side (taller hide shorter). "
                 f"Fill the grid and list all {n * n} heights row by row.\n{grid}"))

    def solve(self):
        ru = self.language == "ru"
        flat = [self.solution[r][c] for r in range(self.n) for c in range(self.n)]
        nums = " ".join(str(x) for x in flat)
        self.solution_steps = [
            ("Клетка с краевым числом 1 содержит максимальную высоту; клетка с числом N — по возрастанию." if ru else
             "A border clue of 1 forces the tallest first; a clue of N forces an increasing line."),
            (f"Решение (по строкам): {nums}." if ru else f"Solution (row by row): {nums}."),
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
