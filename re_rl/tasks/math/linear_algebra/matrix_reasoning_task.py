"""MatrixReasoningTask — базовые характеристики матрицы.

Подтипы: определитель, ранг, след, собственные значения (для целочисленных
матриц с целыми собственными значениями). Ответы числовые/списочные,
верифицируются точно.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class MatrixReasoningTask(BaseMathTask):
    """Определитель / ранг / след / собственные значения матрицы."""

    TASK_TYPE = "matrix_reasoning"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 2, "max_entry": 3, "subtype": "trace"},
        2: {"size": 2, "max_entry": 4, "subtype": "determinant"},
        3: {"size": 2, "max_entry": 5, "subtype": "determinant"},
        4: {"size": 3, "max_entry": 4, "subtype": "rank"},
        5: {"size": 3, "max_entry": 5, "subtype": "determinant"},
        6: {"size": 2, "max_entry": 5, "subtype": "eigenvalues"},
        7: {"size": 3, "max_entry": 6, "subtype": "rank"},
        8: {"size": 3, "max_entry": 6, "subtype": "determinant"},
        9: {"size": 2, "max_entry": 7, "subtype": "eigenvalues"},
        10: {"size": 3, "max_entry": 7, "subtype": "determinant"},
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
        size: Optional[int] = None,
        max_entry: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or preset.get("subtype", "determinant")
        self.size = int(size if size is not None else preset.get("size", 2))
        self.max_entry = int(max_entry if max_entry is not None else preset.get("max_entry", 5))
        self.augment = augment

        self._matrix, self._answer_value = self._build()

        key = self.subtype if self.subtype in {"determinant", "rank", "trace", "eigenvalues"} else "determinant"
        description = get_template(
            PROMPT_TEMPLATES["matrix_reasoning"], key, language,
            augment=False, matrix=self._render_matrix(self._matrix),
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _random_matrix(self) -> sp.Matrix:
        n = self.size
        return sp.Matrix(n, n, lambda i, j: random.randint(-self.max_entry, self.max_entry))

    def _build(self):
        if self.subtype == "eigenvalues":
            # 2x2 с целыми собственными значениями через сопряжение сдвигом.
            l1 = random.randint(-self.max_entry, self.max_entry)
            l2 = random.randint(-self.max_entry, self.max_entry)
            D = sp.Matrix([[l1, 0], [0, l2]])
            T = sp.Matrix([[1, 1], [0, 1]])
            M = T * D * T.inv()
            M = sp.Matrix(M).applyfunc(lambda v: sp.Integer(int(v)))
            return M, sorted([l1, l2])

        M = self._random_matrix()
        if self.subtype == "trace":
            return M, int(M.trace())
        if self.subtype == "rank":
            return M, int(M.rank())
        return M, int(M.det())  # determinant

    @staticmethod
    def _render_matrix(M: sp.Matrix) -> str:
        rows = []
        for i in range(M.rows):
            rows.append("  [" + ", ".join(str(M[i, j]) for j in range(M.cols)) + "]")
        return "\n".join(rows)

    def solve(self):
        section = PROMPT_TEMPLATES["matrix_reasoning"]
        if self.subtype == "eigenvalues":
            result = ", ".join(str(v) for v in self._answer_value)
        else:
            result = str(self._answer_value)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        import re
        from re_rl.rewards import extract_reasoning_and_answer, coerce_float

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction

        if self.subtype == "eigenvalues":
            nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
            pred = sorted(int(round(float(n))) for n in nums)
            return 1.0 if pred == sorted(self._answer_value) else 0.0

        pred = coerce_float(text)
        if pred is None:
            return 0.0
        return 1.0 if abs(pred - float(self._answer_value)) < 1e-6 else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "MatrixReasoningTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
