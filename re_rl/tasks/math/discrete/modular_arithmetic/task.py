"""ModularArithmeticTask — модульное возведение в степень и дискретный логарифм.

Подтипы:
- ``modexp``: вычислить a^b mod m (числовой ответ).
- ``discrete_log``: найти наименьшее x ≥ 0 с g^x ≡ h (mod p) (перебор малого порядка).
"""

import random
import sympy
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ModularArithmeticTask(BaseMathTask):
    """Модульная арифметика: modexp и дискретный логарифм."""

    TASK_TYPE = "modular_arithmetic"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"subtype": "modexp", "max_base": 6, "max_exp": 5, "max_mod": 20},
        2: {"subtype": "modexp", "max_base": 8, "max_exp": 8, "max_mod": 30},
        3: {"subtype": "modexp", "max_base": 10, "max_exp": 12, "max_mod": 50},
        4: {"subtype": "modexp", "max_base": 12, "max_exp": 20, "max_mod": 97},
        5: {"subtype": "discrete_log", "max_prime": 17},
        6: {"subtype": "discrete_log", "max_prime": 23},
        7: {"subtype": "modexp", "max_base": 20, "max_exp": 50, "max_mod": 251},
        8: {"subtype": "discrete_log", "max_prime": 37},
        9: {"subtype": "discrete_log", "max_prime": 53},
        10: {"subtype": "modexp", "max_base": 30, "max_exp": 100, "max_mod": 997},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        subtype: Optional[str] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or preset.get("subtype", "modexp")
        self._preset = preset
        self.augment = augment

        # Параметры задачи
        self.a = self.b = self.m = 0
        self.g = self.h = self.p = 0
        self._answer = 0

        if self.subtype == "discrete_log":
            self._build_discrete_log()
            description = get_template(
                PROMPT_TEMPLATES["modular_arithmetic"], "dlog_problem", language,
                augment=augment, g=self.g, h=self.h, p=self.p,
            )
        else:
            self._build_modexp()
            description = get_template(
                PROMPT_TEMPLATES["modular_arithmetic"], "modexp_problem", language,
                augment=augment, a=self.a, b=self.b, m=self.m,
            )

        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _build_modexp(self):
        self.a = random.randint(2, self._preset.get("max_base", 10))
        self.b = random.randint(2, self._preset.get("max_exp", 12))
        self.m = random.randint(3, self._preset.get("max_mod", 50))
        self._answer = pow(self.a, self.b, self.m)

    def _build_discrete_log(self):
        max_prime = self._preset.get("max_prime", 23)
        primes = list(sympy.primerange(5, max_prime + 1))
        self.p = random.choice(primes) if primes else 7
        self.g = random.randint(2, self.p - 1)
        x = random.randint(1, self.p - 1)
        self.h = pow(self.g, x, self.p)
        # Наименьший неотрицательный показатель.
        self._answer = self._smallest_dlog(self.g, self.h, self.p)

    @staticmethod
    def _smallest_dlog(g: int, h: int, p: int) -> int:
        val = 1 % p
        for x in range(0, p):
            if val == h % p:
                return x
            val = (val * g) % p
        return -1

    def solve(self):
        section = PROMPT_TEMPLATES["modular_arithmetic"]
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=self._answer)
        )
        self.final_answer = str(self._answer)

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction
        nums = re.findall(r"-?\d+", text)
        if not nums:
            return 0.0
        pred = int(nums[0])

        if self.subtype == "discrete_log":
            # Засчитываем любой корректный показатель (g^x ≡ h).
            if pred < 0:
                return 0.0
            return 1.0 if pow(self.g, pred, self.p) == self.h % self.p else 0.0

        return 1.0 if pred == self._answer else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "ModularArithmeticTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
