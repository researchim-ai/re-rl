"""RootsOfUnityTask — все комплексные корни уравнения z^n = R (формула Муавра).

Проверка геометрическая: разбираем список комплексных чисел из ответа и
сопоставляем их с эталонными корнями с точностью tol (нужно ровно n различных
корней, каждый из которых близок к одному из истинных).
"""

import cmath
import math
import random
import re
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class RootsOfUnityTask(BaseMathTask):
    """Найти все корни z^n = R (проверка сопоставлением комплексных корней)."""

    TASK_TYPE = "roots_of_unity"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "rmax": 4}, 2: {"n": 2, "rmax": 9}, 3: {"n": 3, "rmax": 4},
        4: {"n": 3, "rmax": 8}, 5: {"n": 4, "rmax": 4}, 6: {"n": 4, "rmax": 8},
        7: {"n": 5, "rmax": 4}, 8: {"n": 6, "rmax": 4}, 9: {"n": 6, "rmax": 8},
        10: {"n": 8, "rmax": 4},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        n: Optional[int] = None,
        rmax: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(n if n is not None else preset.get("n", 4))
        self.rmax = int(rmax if rmax is not None else preset.get("rmax", 4))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["roots_of_unity"], "problem", language,
            augment=augment, n=self.n, value=self.R,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _build(self):
        self.R = random.randint(1, self.rmax)
        modulus = self.R ** (1.0 / self.n)
        self._roots: List[complex] = [
            cmath.rect(modulus, 2 * math.pi * k / self.n) for k in range(self.n)
        ]

    @staticmethod
    def _fmt(z: complex) -> str:
        a = round(z.real, 4)
        b = round(z.imag, 4)
        if abs(a) < 1e-9:
            a = 0.0
        if abs(b) < 1e-9:
            b = 0.0
        sign = "+" if b >= 0 else "-"
        return f"{a}{sign}{abs(b)}i"

    @staticmethod
    def _parse_complex(tok: str) -> Optional[complex]:
        tok = tok.strip().replace(" ", "").replace("*", "").replace("−", "-")
        if not tok:
            return None
        m = re.search(r"([+-]?\d*\.?\d*)\s*[ij]", tok)
        imag = 0.0
        if m:
            coef = m.group(1)
            if coef in ("", "+"):
                imag = 1.0
            elif coef == "-":
                imag = -1.0
            else:
                try:
                    imag = float(coef)
                except ValueError:
                    return None
            real_str = (tok[:m.start()] + tok[m.end():]).strip("+")
        else:
            real_str = tok
        real = 0.0
        if real_str not in ("", "+", "-"):
            try:
                real = float(real_str)
            except ValueError:
                return None
        return complex(real, imag)

    def solve(self):
        section = PROMPT_TEMPLATES["roots_of_unity"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = "; ".join(self._fmt(z) for z in self._roots)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction)
        tokens = re.split(r"[;,]", text)
        pred = [self._parse_complex(t) for t in tokens]
        pred = [z for z in pred if z is not None]
        if len(pred) != self.n:
            return 0.0
        remaining = list(self._roots)
        tol = 1e-2
        for z in pred:
            match_idx = None
            for i, r in enumerate(remaining):
                if abs(z - r) <= tol:
                    match_idx = i
                    break
            if match_idx is None:
                return 0.0
            remaining.pop(match_idx)
        return 1.0 if not remaining else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "RootsOfUnityTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
