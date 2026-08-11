"""LeastSquaresTask — линейная регрессия методом наименьших квадратов.

По набору точек ищется прямая y = k·x + b. Коэффициенты вычисляются точно
(рациональные числа), проверка числовая: сравниваются k и b.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class LeastSquaresTask(BaseMathTask):
    """Найти прямую y=kx+b методом наименьших квадратов (числовая проверка)."""

    TASK_TYPE = "least_squares"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "coord": 4}, 2: {"n": 3, "coord": 6}, 3: {"n": 4, "coord": 6},
        4: {"n": 4, "coord": 8}, 5: {"n": 5, "coord": 8}, 6: {"n": 5, "coord": 10},
        7: {"n": 6, "coord": 10}, 8: {"n": 6, "coord": 12}, 9: {"n": 7, "coord": 12},
        10: {"n": 8, "coord": 14},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        n: Optional[int] = None,
        coord: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(n if n is not None else preset.get("n", 5))
        self.coord = int(coord if coord is not None else preset.get("coord", 8))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["least_squares"], "problem", language,
            augment=augment, points=self._points_str(),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        xs: List[int] = random.sample(range(-self.coord, self.coord + 1), self.n)
        ys: List[int] = [random.randint(-self.coord, self.coord) for _ in range(self.n)]
        self._points: List[Tuple[int, int]] = list(zip(xs, ys))
        n = self.n
        sx = sum(xs)
        sy = sum(ys)
        sxx = sum(x * x for x in xs)
        sxy = sum(x * y for x, y in zip(xs, ys))
        denom = n * sxx - sx * sx
        self._k = Fraction(n * sxy - sx * sy, denom)
        self._b = Fraction(sy, n) - self._k * Fraction(sx, n)

    def _points_str(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self._points)

    def solve(self):
        section = PROMPT_TEMPLATES["least_squares"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = f"k = {self._k}, b = {self._b}"
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction)
        # Убираем метки, оставляя только числовые значения k и b.
        text = re.sub(r"[kbкб]\s*=", " ", text, flags=re.IGNORECASE)
        nums = extract_numbers(text)
        return 1.0 if numbers_match(nums[:2], [float(self._k), float(self._b)]) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "LeastSquaresTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
