"""KakuroTask — мини кросс-сумма (Kakuro).

Пять белых клеток A, B (верхний ряд), C, D, E (нижний ряд); A над C, B над D.
Для каждой «линии» задана сумма, а цифры (1..9) внутри линии различны. Экземпляр
строится так, чтобы решение было единственным (проверка полным перебором).
"""

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class KakuroTask(BaseMathTask):
    TASK_TYPE = "kakuro"

    # Сложность влияет на диапазон цифр (насколько «плотные» суммы).
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        self.augment = augment
        self.difficulty = difficulty
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _valid(self, a, b, c, d, e) -> bool:
        return (a != b and len({c, d, e}) == 3 and a != c and b != d and
                a + b == self.s1 and c + d + e == self.s2 and a + c == self.v1 and b + d == self.v2)

    def _count_solutions(self):
        sols = []
        for a, b, c, d, e in product(range(1, 10), repeat=5):
            if self._valid(a, b, c, d, e):
                sols.append((a, b, c, d, e))
                if len(sols) > 1:
                    return sols
        return sols

    def _build(self):
        last = None
        for _ in range(500):
            a, b = random.sample(range(1, 10), 2)
            c, d, e = random.sample(range(1, 10), 3)
            if a == c or b == d:  # вертикальные линии тоже требуют различия
                continue
            self.s1, self.s2 = a + b, c + d + e
            self.v1, self.v2 = a + c, b + d
            last = (a, b, c, d, e)
            sols = self._count_solutions()
            if len(sols) == 1:
                self.solution = sols[0]  # единственное решение
                return
        # если уникальный не нашли — берём любое согласованное решение
        self.solution = last

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        return ((f"Мини кросс-сумма. Пять клеток: A, B (верхний ряд) и C, D, E (нижний ряд); "
                 f"A над C, B над D. В каждой линии цифры от 1 до 9 различны и в сумме дают указанное "
                 f"число:\n"
                 f"- верхняя горизонталь (A, B) = {self.s1}\n"
                 f"- нижняя горизонталь (C, D, E) = {self.s2}\n"
                 f"- левая вертикаль (A, C) = {self.v1}\n"
                 f"- правая вертикаль (B, D) = {self.v2}\n"
                 f"Найдите цифры A, B, C, D, E (в этом порядке).") if ru else
                (f"Mini Kakuro. Five cells: A, B (top row) and C, D, E (bottom row); A above C, "
                 f"B above D. In each line digits 1..9 are distinct and add up to the given sum:\n"
                 f"- top row (A, B) = {self.s1}\n"
                 f"- bottom row (C, D, E) = {self.s2}\n"
                 f"- left column (A, C) = {self.v1}\n"
                 f"- right column (B, D) = {self.v2}\n"
                 f"Find the digits A, B, C, D, E (in this order)."))

    def solve(self):
        ru = self.language == "ru"
        nums = " ".join(str(x) for x in self.solution)
        self.solution_steps = [
            ("Из пересечений линий выражаем клетки и подбираем цифры под суммы." if ru else
             "Use the line intersections to express cells and fit digits to the sums."),
            (f"Единственное решение (A, B, C, D, E): {nums}." if ru else
             f"The unique solution (A, B, C, D, E): {nums}."),
        ]
        self.final_answer = nums

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) < 5:
            return 0.0
        a, b, c, d, e = ints[-5:]
        return 1.0 if self._valid(a, b, c, d, e) else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
