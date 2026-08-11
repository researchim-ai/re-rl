"""KenKenTask — головоломка KenKen 4×4.

Латинский квадрат 1..N, дополнительно разбитый на «клетки-клетки» (cages). Для
каждой группы задан результат операции (+, ×, −, ÷) над её числами. Нужно
заполнить сетку. Засчитывается любое заполнение, удовлетворяющее всем клеткам
(латинскость + операции).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_LETTERS = "ABCDEFGHIJKLMNOP"


class KenKenTask(BaseMathTask):
    TASK_TYPE = "kenken"

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

    def _neighbors(self, cell):
        r, c = cell
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.n and 0 <= nc < self.n:
                yield (nr, nc)

    def _partition(self):
        cells = [(r, c) for r in range(self.n) for c in range(self.n)]
        unassigned = set(cells)
        cages = []
        while unassigned:
            start = random.choice(list(unassigned))
            size = random.randint(1, 3)
            cage = [start]
            unassigned.discard(start)
            while len(cage) < size:
                frontier = [nb for cell in cage for nb in self._neighbors(cell) if nb in unassigned]
                if not frontier:
                    break
                nxt = random.choice(frontier)
                cage.append(nxt)
                unassigned.discard(nxt)
            cages.append(cage)
        return cages

    def _cage_clue(self, cage) -> Tuple[str, int]:
        vals = [self.solution[r][c] for (r, c) in cage]
        if len(cage) == 1:
            return ("=", vals[0])
        if len(cage) == 2:
            a, b = sorted(vals, reverse=True)
            ops = ["+", "*", "-"]
            if a % b == 0:
                ops.append("/")
            op = random.choice(ops)
            if op == "+":
                return ("+", a + b)
            if op == "*":
                return ("*", a * b)
            if op == "-":
                return ("-", a - b)
            return ("/", a // b)
        op = random.choice(["+", "*"])
        if op == "+":
            return ("+", sum(vals))
        prod = 1
        for v in vals:
            prod *= v
        return ("*", prod)

    def _build(self):
        self.solution = random.choice(self.squares)
        self.cages = self._partition()
        self.clues = [self._cage_clue(cage) for cage in self.cages]

    def _letter_grid(self):
        gid = {}
        for i, cage in enumerate(self.cages):
            for cell in cage:
                gid[cell] = _LETTERS[i]
        rows = []
        for r in range(self.n):
            rows.append(" ".join(gid[(r, c)] for c in range(self.n)))
        return "\n".join(rows)

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        letter_grid = self._letter_grid()
        clue_lines = []
        for i, (op, target) in enumerate(self.clues):
            sym = {"+": "+", "*": "×", "-": "−", "/": "÷", "=": "="}[op]
            clue_lines.append(f"{_LETTERS[i]}: {target}{sym}" if op != "=" else f"{_LETTERS[i]}: {target}")
        clues = "\n".join(clue_lines)
        return ((f"KenKen {self.n}×{self.n}. В каждой строке и столбце числа 1..{self.n} без "
                 f"повторений. Буквы обозначают группы клеток; для каждой группы указан результат "
                 f"операции над её числами (например, «7+» — сумма 7, «6×» — произведение 6, «2−» — "
                 f"разность 2, «2÷» — частное 2). Заполните сетку и выпишите все {self.n * self.n} "
                 f"чисел по строкам.\nСетка групп:\n{letter_grid}\nПодсказки:\n{clues}") if ru else
                (f"{self.n}×{self.n} KenKen. Each row and column has 1..{self.n} once. Letters mark "
                 f"cages; each cage shows the result of an operation on its numbers (e.g. '7+' sum 7, "
                 f"'6×' product 6, '2−' difference 2, '2÷' quotient 2). Fill the grid and list all "
                 f"{self.n * self.n} numbers row by row.\nCage grid:\n{letter_grid}\nClues:\n{clues}"))

    def solve(self):
        ru = self.language == "ru"
        flat = [self.solution[r][c] for r in range(self.n) for c in range(self.n)]
        nums = " ".join(str(x) for x in flat)
        self.solution_steps = [
            ("Совмещаем ограничение латинского квадрата с арифметикой каждой группы." if ru else
             "Combine the Latin-square constraint with each cage's arithmetic."),
            (f"Решение (по строкам): {nums}." if ru else f"Solution (row by row): {nums}."),
        ]
        self.final_answer = nums

    def _cage_ok(self, grid, cage, clue) -> bool:
        op, target = clue
        vals = [grid[r][c] for (r, c) in cage]
        if op == "=":
            return vals[0] == target
        if op == "+":
            return sum(vals) == target
        if op == "*":
            prod = 1
            for v in vals:
                prod *= v
            return prod == target
        a, b = max(vals), min(vals)
        if op == "-":
            return a - b == target
        return b != 0 and a % b == 0 and a // b == target

    def _check_grid(self, flat: List[int]) -> bool:
        n = self.n
        if len(flat) != n * n or any(v < 1 or v > n for v in flat):
            return False
        grid = [flat[r * n:(r + 1) * n] for r in range(n)]
        for i in range(n):
            if sorted(grid[i]) != list(range(1, n + 1)):
                return False
            if sorted(grid[r][i] for r in range(n)) != list(range(1, n + 1)):
                return False
        return all(self._cage_ok(grid, cage, clue) for cage, clue in zip(self.cages, self.clues))

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
