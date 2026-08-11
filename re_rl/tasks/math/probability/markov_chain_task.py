"""MarkovChainTask — стационарное распределение цепи Маркова.

Матрица переходов строится строго положительной (эргодической), поэтому
стационарное распределение единственно. Вычисляется точно через sympy,
проверка числовая (сравнение вектора π).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class MarkovChainTask(BaseMathTask):
    """Найти стационарное распределение цепи Маркова (числовая проверка)."""

    TASK_TYPE = "markov_chain"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 2, "denom": 5}, 2: {"size": 2, "denom": 6}, 3: {"size": 2, "denom": 8},
        4: {"size": 2, "denom": 10}, 5: {"size": 3, "denom": 6}, 6: {"size": 3, "denom": 8},
        7: {"size": 3, "denom": 10}, 8: {"size": 3, "denom": 12}, 9: {"size": 4, "denom": 8},
        10: {"size": 4, "denom": 10},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        size: Optional[int] = None,
        denom: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.size = int(size if size is not None else preset.get("size", 3))
        self.denom = int(denom if denom is not None else preset.get("denom", 8))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["markov_chain"], "problem", language,
            augment=augment, matrix=self._matrix_str(),
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        n = self.size
        rows = []
        for _ in range(n):
            # Положительные веса -> строго положительная строка (эргодичность).
            weights = [random.randint(1, self.denom) for _ in range(n)]
            s = sum(weights)
            rows.append([sp.Rational(w, s) for w in weights])
        self._P = sp.Matrix(rows)

        # Стационарное: πP = π, Σπ = 1. Решаем (P^T - I)π = 0 с нормировкой.
        A = (self._P.T - sp.eye(n))
        ns = A.nullspace()
        vec = ns[0]
        vec = vec / sum(vec)
        self._pi = [sp.nsimplify(v) for v in vec]
        self._pi_float: List[float] = [float(v) for v in vec]

    def _matrix_str(self) -> str:
        n = self.size
        return "\n".join("[" + ", ".join(str(self._P[i, j]) for j in range(n)) + "]"
                         for i in range(n))

    def solve(self):
        section = PROMPT_TEMPLATES["markov_chain"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = "π = (" + ", ".join(str(v) for v in self._pi) + ")"
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text, extract_numbers, numbers_match

        if self.final_answer is None:
            self.solve()
        nums = extract_numbers(extract_answer_text(prediction))
        return 1.0 if numbers_match(nums, self._pi_float, tol=1e-4) else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "MarkovChainTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
