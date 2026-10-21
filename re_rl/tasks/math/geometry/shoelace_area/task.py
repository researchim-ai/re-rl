"""ShoelaceAreaTask — площадь простого многоугольника по координатам вершин.

Многоугольник строится звёздчато-выпуклым (вершины сортируются по полярному углу
вокруг центра), поэтому он несамопересекающийся. Площадь считается формулой
Гаусса (шнурков) точно; проверка числовая.
"""

import math
import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ShoelaceAreaTask(BaseMathTask):
    """Площадь многоугольника по вершинам (формула шнурков)."""

    TASK_TYPE = "shoelace_area"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "coord": 5}, 2: {"n": 3, "coord": 7}, 3: {"n": 4, "coord": 7},
        4: {"n": 4, "coord": 9}, 5: {"n": 5, "coord": 9}, 6: {"n": 5, "coord": 11},
        7: {"n": 6, "coord": 11}, 8: {"n": 6, "coord": 13}, 9: {"n": 7, "coord": 13},
        10: {"n": 8, "coord": 15},
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
        self.coord = int(coord if coord is not None else preset.get("coord", 9))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["shoelace_area"], "problem", language,
            augment=augment, points=self._points_str(),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        pts: set = set()
        while len(pts) < self.n:
            pts.add((random.randint(-self.coord, self.coord),
                     random.randint(-self.coord, self.coord)))
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        self._points: List[Tuple[int, int]] = sorted(
            pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx)
        )
        s = 0
        m = len(self._points)
        for i in range(m):
            x1, y1 = self._points[i]
            x2, y2 = self._points[(i + 1) % m]
            s += x1 * y2 - x2 * y1
        self._area = Fraction(abs(s), 2)

    def _points_str(self) -> str:
        return ", ".join(f"({x}, {y})" for x, y in self._points)

    def solve(self):
        section = PROMPT_TEMPLATES["shoelace_area"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._area)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], [float(self._area)]) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ShoelaceAreaTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
