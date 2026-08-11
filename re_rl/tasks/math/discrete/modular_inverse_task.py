"""ModularInverseTask — обратный элемент по модулю (расширенный Евклид).

Модуль и число взаимно просты, поэтому обратный существует и единственен в
диапазоне 0..m-1. Проверка принимает любой представитель класса вычетов, для
которого a·x ≡ 1 (mod m).
"""

import math
import random
import re
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ModularInverseTask(BaseMathTask):
    """Найти a⁻¹ (mod m)."""

    TASK_TYPE = "modular_inverse"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mod_max": 11}, 2: {"mod_max": 17}, 3: {"mod_max": 23}, 4: {"mod_max": 31},
        5: {"mod_max": 47}, 6: {"mod_max": 67}, 7: {"mod_max": 97}, 8: {"mod_max": 131},
        9: {"mod_max": 197}, 10: {"mod_max": 251},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        mod_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.mod_max = int(mod_max if mod_max is not None else preset.get("mod_max", 47))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["modular_inverse"], "problem", language,
            augment=augment, a=self.a, m=self.m, m1=self.m - 1,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        while True:
            self.m = random.randint(5, self.mod_max)
            self.a = random.randint(2, self.m - 1)
            if math.gcd(self.a, self.m) == 1:
                break
        self._inv = pow(self.a, -1, self.m)

    def solve(self):
        section = PROMPT_TEMPLATES["modular_inverse"]
        self.solution_steps.append(
            get_template(section, "step_setup", self.language, augment=False, a=self.a, m=self.m)
        )
        result = str(self._inv)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).replace("−", "-")
        nums = re.findall(r"-?\d+", text)
        if not nums:
            return 0.0
        x = int(nums[0])
        return 1.0 if (self.a * x) % self.m == 1 % self.m else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ModularInverseTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
