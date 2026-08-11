"""MatrixMultiplicationTask — произведение двух матриц.

Числовая проверка: все числа ответа сравниваются с элементами матрицы-произведения
в построчном порядке.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class MatrixMultiplicationTask(BaseMathTask):
    """Перемножить матрицы A·B (числовая проверка)."""

    TASK_TYPE = "matrix_multiplication"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"dim": 2, "coef": 3}, 2: {"dim": 2, "coef": 5}, 3: {"dim": 2, "coef": 7},
        4: {"dim": 2, "coef": 9}, 5: {"dim": 3, "coef": 4}, 6: {"dim": 3, "coef": 6},
        7: {"dim": 3, "coef": 8}, 8: {"dim": 3, "coef": 10}, 9: {"dim": 4, "coef": 6},
        10: {"dim": 4, "coef": 9},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        dim: Optional[int] = None,
        coef: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.dim = int(dim if dim is not None else preset.get("dim", 3))
        self.coef = int(coef if coef is not None else preset.get("coef", 6))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["matrix_multiplication"], "problem", language,
            augment=augment, a=self._fmt(self._A), b=self._fmt(self._B),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        n = self.dim
        rnd = lambda: [[random.randint(-self.coef, self.coef) for _ in range(n)] for _ in range(n)]
        self._A = sp.Matrix(rnd())
        self._B = sp.Matrix(rnd())
        self._C = self._A * self._B
        self._flat: List[float] = [float(v) for v in self._C]

    @staticmethod
    def _fmt(m: sp.Matrix) -> str:
        return "\n".join("[" + ", ".join(str(m[i, j]) for j in range(m.cols)) + "]"
                         for i in range(m.rows))

    def solve(self):
        section = PROMPT_TEMPLATES["matrix_multiplication"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._fmt(self._C).replace("\n", "; ")
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums, self._flat) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "MatrixMultiplicationTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
