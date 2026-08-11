"""TriangleSolvingTask — решение треугольника по теоремам синусов/косинусов.

Подтипы подобраны так, чтобы ответ был целым/рациональным:
- ``law_cosines``: c² = a² + b² − 2ab·cos(θ), θ ∈ {60°, 90°, 120°} (cos ∈ {½,0,−½}).
- ``hypotenuse_sq``: квадрат гипотенузы прямоугольного треугольника a² + b².
- ``right_area``: площадь прямоугольного треугольника с катетами a, b.
Проверка числовая.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class TriangleSolvingTask(BaseMathTask):
    """Решение треугольника (числовая проверка)."""

    TASK_TYPE = "triangle_solving"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"side_max": 6}, 2: {"side_max": 8}, 3: {"side_max": 10}, 4: {"side_max": 12},
        5: {"side_max": 15}, 6: {"side_max": 18}, 7: {"side_max": 22}, 8: {"side_max": 26},
        9: {"side_max": 30}, 10: {"side_max": 40},
    }

    _COS = {60: Fraction(1, 2), 90: Fraction(0), 120: Fraction(-1, 2)}

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        side_max: Optional[int] = None,
        subtype: Optional[str] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.side_max = int(side_max if side_max is not None else preset.get("side_max", 15))
        self.subtype = subtype or random.choice(["law_cosines", "hypotenuse_sq", "right_area"])
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["triangle_solving"], "problem", language,
            augment=augment, scenario=self._scenario(language),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.a = random.randint(2, self.side_max)
        self.b = random.randint(2, self.side_max)
        if self.subtype == "law_cosines":
            self.theta = random.choice([60, 90, 120])
            self._val = Fraction(self.a ** 2 + self.b ** 2) - 2 * self.a * self.b * self._COS[self.theta]
        elif self.subtype == "hypotenuse_sq":
            self._val = Fraction(self.a ** 2 + self.b ** 2)
        else:  # right_area
            self._val = Fraction(self.a * self.b, 2)
        self._ref: List[float] = [float(self._val)]
        self._answer_str = str(self._val)

    def _scenario(self, language: str) -> str:
        if language == "ru":
            if self.subtype == "law_cosines":
                return (f"В треугольнике две стороны равны {self.a} и {self.b}, "
                        f"а угол между ними {self.theta}°. Найдите квадрат третьей стороны.")
            if self.subtype == "hypotenuse_sq":
                return (f"В прямоугольном треугольнике катеты равны {self.a} и {self.b}. "
                        f"Найдите квадрат гипотенузы.")
            return (f"В прямоугольном треугольнике катеты равны {self.a} и {self.b}. "
                    f"Найдите площадь треугольника.")
        if self.subtype == "law_cosines":
            return (f"A triangle has two sides {self.a} and {self.b} with the included "
                    f"angle {self.theta}°. Find the square of the third side.")
        if self.subtype == "hypotenuse_sq":
            return (f"A right triangle has legs {self.a} and {self.b}. "
                    f"Find the square of the hypotenuse.")
        return (f"A right triangle has legs {self.a} and {self.b}. Find its area.")

    def solve(self):
        section = PROMPT_TEMPLATES["triangle_solving"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=self._answer_str)
        )
        self.final_answer = self._answer_str

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], self._ref) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "TriangleSolvingTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
