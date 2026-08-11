"""GramSchmidtTask — ортогонализация системы векторов методом Грама–Шмидта.

Проверка геометрическая: предъявленные векторы должны быть попарно ортогональны,
ненулевые, в нужном количестве и порождать то же подпространство, что и исходные
(любой корректный ортогональный базис засчитывается, масштаб не важен).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class GramSchmidtTask(BaseMathTask):
    """Ортогонализовать систему векторов (проверка ортогональности и оболочки)."""

    TASK_TYPE = "gram_schmidt"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"dim": 2, "k": 2, "coef": 3}, 2: {"dim": 2, "k": 2, "coef": 4},
        3: {"dim": 2, "k": 2, "coef": 5}, 4: {"dim": 3, "k": 2, "coef": 3},
        5: {"dim": 3, "k": 2, "coef": 4}, 6: {"dim": 3, "k": 3, "coef": 3},
        7: {"dim": 3, "k": 3, "coef": 4}, 8: {"dim": 3, "k": 3, "coef": 5},
        9: {"dim": 4, "k": 3, "coef": 4}, 10: {"dim": 4, "k": 4, "coef": 4},
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
        k: Optional[int] = None,
        coef: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.dim = int(dim if dim is not None else preset.get("dim", 3))
        self.k = int(k if k is not None else preset.get("k", 2))
        self.k = min(self.k, self.dim)
        self.coef = int(coef if coef is not None else preset.get("coef", 4))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["gram_schmidt"], "problem", language,
            augment=augment, vectors=self._fmt_vectors(self._vectors),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        while True:
            vecs = [sp.Matrix([random.randint(-self.coef, self.coef) for _ in range(self.dim)])
                    for _ in range(self.k)]
            M = sp.Matrix.hstack(*vecs)
            if M.rank() == self.k:  # линейная независимость
                break
        self._vectors = vecs
        self._ortho = sp.GramSchmidt(vecs)

    @staticmethod
    def _fmt_vectors(vecs: List[sp.Matrix]) -> str:
        return ", ".join("(" + ", ".join(str(v[i]) for i in range(v.rows)) + ")" for v in vecs)

    def solve(self):
        section = PROMPT_TEMPLATES["gram_schmidt"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._fmt_vectors(self._ortho)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        import numpy as np
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        if len(nums) != self.dim * self.k:
            return 0.0
        pred_vecs = [np.array(nums[i * self.dim:(i + 1) * self.dim], dtype=float)
                     for i in range(self.k)]

        # Ни один вектор не нулевой.
        for v in pred_vecs:
            if np.linalg.norm(v) < 1e-9:
                return 0.0
        # Попарная ортогональность.
        for i in range(self.k):
            for j in range(i + 1, self.k):
                if abs(float(pred_vecs[i] @ pred_vecs[j])) > 1e-6:
                    return 0.0
        # Та же линейная оболочка, что у исходных векторов.
        orig = np.array([[float(v[r]) for v in self._vectors] for r in range(self.dim)])
        pred = np.column_stack(pred_vecs)
        combined = np.hstack([orig, pred])
        tol = 1e-6
        if not (np.linalg.matrix_rank(orig, tol=tol) ==
                np.linalg.matrix_rank(pred, tol=tol) ==
                np.linalg.matrix_rank(combined, tol=tol) == self.k):
            return 0.0
        return 1.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "GramSchmidtTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
