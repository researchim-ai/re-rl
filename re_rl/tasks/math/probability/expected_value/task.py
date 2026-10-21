"""ExpectedValueTask — математическое ожидание дискретной случайной величины.

E[X] = Σ xᵢ·pᵢ вычисляется точно (рациональное число). Проверка числовая.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ExpectedValueTask(BaseMathTask):
    """Найти E[X] дискретной случайной величины (точный расчёт)."""

    TASK_TYPE = "expected_value"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 2, "vmax": 6, "wmax": 4}, 2: {"k": 3, "vmax": 6, "wmax": 4},
        3: {"k": 3, "vmax": 8, "wmax": 5}, 4: {"k": 4, "vmax": 8, "wmax": 5},
        5: {"k": 4, "vmax": 10, "wmax": 6}, 6: {"k": 5, "vmax": 10, "wmax": 6},
        7: {"k": 5, "vmax": 12, "wmax": 7}, 8: {"k": 6, "vmax": 12, "wmax": 8},
        9: {"k": 6, "vmax": 15, "wmax": 9}, 10: {"k": 7, "vmax": 15, "wmax": 10},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        k: Optional[int] = None,
        vmax: Optional[int] = None,
        wmax: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.k = int(k if k is not None else preset.get("k", 4))
        self.vmax = int(vmax if vmax is not None else preset.get("vmax", 10))
        self.wmax = int(wmax if wmax is not None else preset.get("wmax", 6))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["expected_value"], "problem", language,
            augment=augment, values=self._values_str(), probs=self._probs_str(),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.values: List[int] = random.sample(range(-self.vmax, self.vmax + 1), self.k)
        self.weights: List[int] = [random.randint(1, self.wmax) for _ in range(self.k)]
        self.total = sum(self.weights)
        self._ev = sum(Fraction(v * w, self.total) for v, w in zip(self.values, self.weights))

    def _values_str(self) -> str:
        return ", ".join(str(v) for v in self.values)

    def _probs_str(self) -> str:
        return ", ".join(f"{w}/{self.total}" for w in self.weights)

    def solve(self):
        section = PROMPT_TEMPLATES["expected_value"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = str(self._ev)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums[-1:], [float(self._ev)]) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ExpectedValueTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
