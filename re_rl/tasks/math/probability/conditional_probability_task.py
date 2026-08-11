"""ConditionalProbabilityTask — условная вероятность и формула Байеса.

Двухступенчатая схема: заданы P(A), P(B|A), P(B|¬A); требуется P(A|B). Ответ
вычисляется точно (рациональное число), проверка числовая.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ConditionalProbabilityTask(BaseMathTask):
    """Найти P(A|B) по формуле Байеса (точный расчёт)."""

    TASK_TYPE = "conditional_probability"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"denom": 5}, 2: {"denom": 6}, 3: {"denom": 8}, 4: {"denom": 10},
        5: {"denom": 10}, 6: {"denom": 12}, 7: {"denom": 15}, 8: {"denom": 16},
        9: {"denom": 20}, 10: {"denom": 25},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        denom: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.denom = int(denom if denom is not None else preset.get("denom", 10))
        self.augment = augment

        self._build()
        scenario = self._scenario_text(language)
        description = get_template(
            PROMPT_TEMPLATES["conditional_probability"], "problem", language,
            augment=augment, scenario=scenario, event="A|B",
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        d = self.denom
        self.p_a = Fraction(random.randint(1, d - 1), d)
        self.p_b_a = Fraction(random.randint(1, d - 1), d)
        self.p_b_na = Fraction(random.randint(1, d - 1), d)
        p_b = self.p_a * self.p_b_a + (1 - self.p_a) * self.p_b_na
        self._ans = (self.p_a * self.p_b_a) / p_b

    def _scenario_text(self, language: str) -> str:
        if language == "ru":
            return (f"Дано: P(A) = {self.p_a}, P(B|A) = {self.p_b_a}, "
                    f"P(B|¬A) = {self.p_b_na}.")
        return (f"Given: P(A) = {self.p_a}, P(B|A) = {self.p_b_a}, "
                f"P(B|¬A) = {self.p_b_na}.")

    def solve(self):
        section = PROMPT_TEMPLATES["conditional_probability"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._ans)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], [float(self._ans)], tol=1e-3) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ConditionalProbabilityTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
