"""HypothesisTestingTask — двусторонний z-тест для среднего при известном σ.

Считается статистика z и сравнивается с критическим значением; ответ —
решение «reject» или «not reject». Параметры подбираются так, чтобы |z| не
попадало в узкую окрестность критического значения (нет пограничных случаев).
"""

import math
import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


_Z_CRIT = {0.05: 1.959963985, 0.01: 2.575829304, 0.10: 1.644853627}


class HypothesisTestingTask(BaseMathTask):
    """Двусторонний z-тест: reject / not reject (точное решение)."""

    TASK_TYPE = "hypothesis_testing"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"nmax": 25, "sigma_max": 5}, 2: {"nmax": 30, "sigma_max": 6},
        3: {"nmax": 36, "sigma_max": 6}, 4: {"nmax": 49, "sigma_max": 8},
        5: {"nmax": 64, "sigma_max": 8}, 6: {"nmax": 81, "sigma_max": 10},
        7: {"nmax": 100, "sigma_max": 10}, 8: {"nmax": 121, "sigma_max": 12},
        9: {"nmax": 144, "sigma_max": 12}, 10: {"nmax": 169, "sigma_max": 15},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        nmax: Optional[int] = None,
        sigma_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.nmax = int(nmax if nmax is not None else preset.get("nmax", 64))
        self.sigma_max = int(sigma_max if sigma_max is not None else preset.get("sigma_max", 8))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["hypothesis_testing"], "problem", language,
            augment=augment, n=self.n, mean=self.mean, mu0=self.mu0,
            sigma=self.sigma, alpha=self.alpha,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.alpha = random.choice([0.05, 0.01, 0.10])
        zc = _Z_CRIT[self.alpha]
        while True:
            self.n = random.choice([k * k for k in range(4, int(self.nmax ** 0.5) + 1)])
            self.sigma = random.randint(2, self.sigma_max)
            self.mu0 = random.randint(20, 60)
            self.mean = self.mu0 + random.randint(-6, 6)
            self.z = (self.mean - self.mu0) * math.sqrt(self.n) / self.sigma
            # Избегаем пограничной зоны вокруг критического значения.
            if abs(abs(self.z) - zc) > 0.25:
                break
        self._reject = abs(self.z) > zc
        self._decision = "reject" if self._reject else "not reject"

    def solve(self):
        section = PROMPT_TEMPLATES["hypothesis_testing"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=self._decision)
        )
        self.final_answer = self._decision

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).strip().lower()
        neg_markers = ["not reject", "not_reject", "fail to reject", "не отвергаем",
                       "не отвергается", "не отклоняем", "принимаем", "accept"]
        is_neg = any(m in text for m in neg_markers)
        if is_neg:
            pred_reject = False
        elif "reject" in text or "отверг" in text or "отклон" in text:
            pred_reject = True
        else:
            return 0.0
        return 1.0 if pred_reject == self._reject else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "HypothesisTestingTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
