"""NQueensTask — задача о ферзях.

Подтипы:
- solve: расставить n ферзей на доске n×n без взаимных боёв (проверяется
  корректность любой валидной расстановки);
- count: число решений задачи о ферзях для данного n (перебор с возвратом).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class NQueensTask(BaseMathTask):
    TASK_TYPE = "n_queens"
    TASK_TYPES = ["solve", "count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 7}, 9: {"n": 8}, 10: {"n": 8},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _solve_all(self, count_only: bool, want_one: bool = False):
        n = self.n
        results = []
        cols, d1, d2 = set(), set(), set()
        placement = []

        def bt(r):
            if r == n:
                results.append(tuple(placement))
                return True if want_one else None
            for c in range(n):
                if c in cols or (r - c) in d1 or (r + c) in d2:
                    continue
                cols.add(c); d1.add(r - c); d2.add(r + c); placement.append(c)
                done = bt(r + 1)
                cols.discard(c); d1.discard(r - c); d2.discard(r + c); placement.pop()
                if done and want_one:
                    return True
            return False

        bt(0)
        return results

    def _build(self):
        if self.subtype == "count":
            self._count = len(self._solve_all(count_only=True))
        else:
            one = self._solve_all(count_only=False, want_one=True)
            self.solution = list(one[0])  # столбцы (0-инд.) для строк 0..n-1

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        if self.subtype == "count":
            return (f"Сколько существует различных расстановок {self.n} ферзей на доске "
                    f"{self.n}×{self.n}, при которых ферзи не бьют друг друга?" if ru else
                    f"How many distinct ways are there to place {self.n} non-attacking queens on an "
                    f"{self.n}×{self.n} board?")
        return (f"Расставьте {self.n} ферзей на доске {self.n}×{self.n} так, чтобы никакие два не "
                f"били друг друга. Для каждой строки сверху вниз укажите номер столбца (1..{self.n}), "
                f"где стоит ферзь — {self.n} чисел по порядку." if ru else
                f"Place {self.n} non-attacking queens on an {self.n}×{self.n} board. For each row from "
                f"top to bottom, give the column (1..{self.n}) of its queen — {self.n} numbers in order.")

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "count":
            self.solution_steps = [
                ("Перебор с возвратом по строкам, отсекая занятые столбцы и диагонали." if ru else
                 "Backtracking row by row, pruning used columns and diagonals."),
                (f"Число решений = {self._count}." if ru else f"Number of solutions = {self._count}."),
            ]
            self.final_answer = str(self._count)
        else:
            cols_1 = [c + 1 for c in self.solution]
            self.solution_steps = [
                ("Ставим ферзей по строкам, выбирая свободный столбец и диагонали." if ru else
                 "Place queens row by row, choosing a free column and diagonals."),
                (f"Одно из решений (столбцы по строкам): {', '.join(map(str, cols_1))}." if ru else
                 f"One solution (columns per row): {', '.join(map(str, cols_1))}."),
            ]
            self.final_answer = " ".join(map(str, cols_1))

    def _valid_placement(self, cols_1: List[int]) -> bool:
        n = self.n
        if len(cols_1) != n:
            return False
        if any(c < 1 or c > n for c in cols_1):
            return False
        cols = [c - 1 for c in cols_1]
        if len(set(cols)) != n:
            return False
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                if abs(cols[r1] - cols[r2]) == abs(r1 - r2):
                    return False
        return True

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.subtype == "count":
            return U.verify_int(prediction, int(self._count))
        ints = U.parse_ints(prediction)
        if len(ints) < self.n:
            return 0.0
        return 1.0 if self._valid_placement(ints[-self.n:]) else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
