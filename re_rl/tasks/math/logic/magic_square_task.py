"""MagicSquareTask — заполнение магического квадрата 3×3.

Дан частично заполненный магический квадрат из чисел 1..9 (суммы по строкам,
столбцам и диагоналям равны 15). Нужно восстановить пропуски. Единственность
гарантируется: все магические квадраты 3×3 — это 8 симметрий базового.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_BASE = (2, 7, 6, 9, 5, 1, 4, 3, 8)


def _rot90(g):
    return (g[6], g[3], g[0], g[7], g[4], g[1], g[8], g[5], g[2])


def _reflect(g):
    return (g[2], g[1], g[0], g[5], g[4], g[3], g[8], g[7], g[6])


def _all_squares():
    seen = set()
    g = _BASE
    for _ in range(4):
        seen.add(g)
        seen.add(_reflect(g))
        g = _rot90(g)
    return list(seen)


class MagicSquareTask(BaseMathTask):
    TASK_TYPE = "magic_square"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"blanks": 2}, 2: {"blanks": 3}, 3: {"blanks": 3}, 4: {"blanks": 4},
        5: {"blanks": 4}, 6: {"blanks": 5}, 7: {"blanks": 5}, 8: {"blanks": 6},
        9: {"blanks": 6}, 10: {"blanks": 7},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.blanks = int(preset["blanks"])
        self.augment = augment
        self.all_squares = _all_squares()
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        self.solution = random.choice(self.all_squares)
        blanks = self.blanks
        for _ in range(200):
            hidden = set(random.sample(range(9), blanks))
            revealed = [p for p in range(9) if p not in hidden]
            matches = [sq for sq in self.all_squares
                       if all(sq[p] == self.solution[p] for p in revealed)]
            if len(matches) == 1:
                self.hidden = hidden
                return
        # уменьшаем число пропусков до достижения уникальности
        for b in range(blanks - 1, 0, -1):
            for _ in range(200):
                hidden = set(random.sample(range(9), b))
                revealed = [p for p in range(9) if p not in hidden]
                matches = [sq for sq in self.all_squares
                           if all(sq[p] == self.solution[p] for p in revealed)]
                if len(matches) == 1:
                    self.hidden = hidden
                    return
        self.hidden = set()

    def _grid_str(self) -> str:
        rows = []
        for r in range(3):
            row = []
            for c in range(3):
                p = r * 3 + c
                row.append("?" if p in self.hidden else str(self.solution[p]))
            rows.append(" ".join(f"{x:>1}" for x in row))
        return "\n".join(rows)

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        return ((f"Магический квадрат 3×3 из чисел 1..9 (каждое по разу); суммы по всем строкам, "
                 f"столбцам и двум диагоналям равны 15. Заполните пропуски «?» и выпишите все 9 "
                 f"чисел по строкам сверху вниз.\n{self._grid_str()}") if ru else
                (f"A 3×3 magic square using numbers 1..9 (each once); every row, column and both "
                 f"diagonals sum to 15. Fill the blanks «?» and write all 9 numbers row by row.\n"
                 f"{self._grid_str()}"))

    def solve(self):
        ru = self.language == "ru"
        nums = " ".join(str(x) for x in self.solution)
        self.solution_steps = [
            ("Используем, что все линии дают 15, и что центр равен 5." if ru else
             "Use that every line sums to 15 and the center is 5."),
            (f"Заполненный квадрат: {nums}." if ru else f"The completed square: {nums}."),
        ]
        self.final_answer = nums

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) < 9:
            return 0.0
        return 1.0 if tuple(ints[-9:]) == self.solution else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
