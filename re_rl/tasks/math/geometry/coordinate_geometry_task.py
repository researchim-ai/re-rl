"""CoordinateGeometryTask — базовые задачи аналитической геометрии на плоскости.

Подтипы: наклон прямой через две точки, квадрат расстояния, середина отрезка.
Все ответы рациональные/целые, проверка числовая.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class CoordinateGeometryTask(BaseMathTask):
    """Аналитическая геометрия: наклон, расстояние², середина (числовая проверка)."""

    TASK_TYPE = "coordinate_geometry"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"coord": 5}, 2: {"coord": 7}, 3: {"coord": 9}, 4: {"coord": 11},
        5: {"coord": 13}, 6: {"coord": 15}, 7: {"coord": 18}, 8: {"coord": 22},
        9: {"coord": 26}, 10: {"coord": 30},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        coord: Optional[int] = None,
        subtype: Optional[str] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.coord = int(coord if coord is not None else preset.get("coord", 13))
        self.subtype = subtype or random.choice(["slope", "distance_sq", "midpoint"])
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["coordinate_geometry"], "problem", language,
            augment=augment, scenario=self._scenario(language),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _rp(self):
        return random.randint(-self.coord, self.coord)

    def _build(self):
        self.x1, self.y1 = self._rp(), self._rp()
        self.x2, self.y2 = self._rp(), self._rp()
        if self.subtype == "slope":
            while self.x2 == self.x1:
                self.x2 = self._rp()
            self._k = Fraction(self.y2 - self.y1, self.x2 - self.x1)
            self._ref: List[float] = [float(self._k)]
            self._answer_str = str(self._k)
        elif self.subtype == "distance_sq":
            d2 = (self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2
            self._ref = [float(d2)]
            self._answer_str = str(d2)
        else:  # midpoint
            mx = Fraction(self.x1 + self.x2, 2)
            my = Fraction(self.y1 + self.y2, 2)
            self._ref = [float(mx), float(my)]
            self._answer_str = f"({mx}, {my})"

    def _scenario(self, language: str) -> str:
        p1 = f"A({self.x1}, {self.y1})"
        p2 = f"B({self.x2}, {self.y2})"
        if language == "ru":
            if self.subtype == "slope":
                return f"Найдите угловой коэффициент прямой, проходящей через точки {p1} и {p2}."
            if self.subtype == "distance_sq":
                return f"Найдите квадрат расстояния между точками {p1} и {p2}."
            return f"Найдите координаты середины отрезка с концами {p1} и {p2}."
        if self.subtype == "slope":
            return f"Find the slope of the line through the points {p1} and {p2}."
        if self.subtype == "distance_sq":
            return f"Find the squared distance between the points {p1} and {p2}."
        return f"Find the midpoint of the segment with endpoints {p1} and {p2}."

    def solve(self):
        section = PROMPT_TEMPLATES["coordinate_geometry"]
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
        return 1.0 if numbers_match(nums[-len(self._ref):], self._ref) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "CoordinateGeometryTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
