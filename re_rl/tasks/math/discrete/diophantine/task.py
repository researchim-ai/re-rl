"""DiophantineTask — линейное диофантово уравнение a·x + b·y = c.

Уравнение всегда разрешимо (c кратно gcd(a,b)). Проверка принимает ЛЮБОЕ
корректное целочисленное решение (x, y).
"""

import math
import random
import re
from typing import Any, ClassVar, Dict, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


def _ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = _ext_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


class DiophantineTask(BaseMathTask):
    """Найти целочисленное решение a·x + b·y = c (расширенный Евклид)."""

    TASK_TYPE = "diophantine"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"coef_max": 6}, 2: {"coef_max": 9}, 3: {"coef_max": 12}, 4: {"coef_max": 15},
        5: {"coef_max": 20}, 6: {"coef_max": 30}, 7: {"coef_max": 45}, 8: {"coef_max": 60},
        9: {"coef_max": 80}, 10: {"coef_max": 100},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        coef_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.coef_max = int(coef_max if coef_max is not None else preset.get("coef_max", 20))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["diophantine"], "problem", language,
            augment=augment, a=self.a, b=self.b, c=self.c,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.a = random.randint(2, self.coef_max)
        self.b = random.randint(2, self.coef_max)
        g = math.gcd(self.a, self.b)
        mult = random.randint(1, 6)
        self.c = g * mult  # гарантированная разрешимость
        _, x0, y0 = _ext_gcd(self.a, self.b)
        self.x_sol = x0 * (self.c // g)
        self.y_sol = y0 * (self.c // g)

    def solve(self):
        section = PROMPT_TEMPLATES["diophantine"]
        self.solution_steps.append(
            get_template(section, "step_setup", self.language, augment=False,
                         a=self.a, b=self.b, c=self.c)
        )
        result = f"(x={self.x_sol}, y={self.y_sol})"
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).replace("−", "-")
        nums = [int(t) for t in re.findall(r"-?\d+", text)]
        if len(nums) < 2:
            return 0.0
        # Пытаемся найти пару, дающую верное равенство (учитывая метки x=, y=).
        x, y = nums[0], nums[1]
        return 1.0 if self.a * x + self.b * y == self.c else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "DiophantineTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
