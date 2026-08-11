"""PrimeFactorizationTask — разложение числа на простые множители.

Проверка принимает любой корректный формат записи (``2^3 * 3 * 5``,
``2*2*2*3*5`` и т. п.): парсит множители, проверяет, что все они простые и их
произведение равно исходному числу.
"""

import random
import re
from typing import Any, ClassVar, Dict, List, Optional

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class PrimeFactorizationTask(BaseMathTask):
    """Разложить число на простые множители (точная проверка)."""

    TASK_TYPE = "prime_factorization"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_primes": 2, "prime_max": 7}, 2: {"num_primes": 2, "prime_max": 11},
        3: {"num_primes": 3, "prime_max": 13}, 4: {"num_primes": 3, "prime_max": 17},
        5: {"num_primes": 3, "prime_max": 23}, 6: {"num_primes": 4, "prime_max": 23},
        7: {"num_primes": 4, "prime_max": 31}, 8: {"num_primes": 4, "prime_max": 41},
        9: {"num_primes": 5, "prime_max": 41}, 10: {"num_primes": 5, "prime_max": 53},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_primes: Optional[int] = None,
        prime_max: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_primes = int(num_primes if num_primes is not None else preset.get("num_primes", 3))
        self.prime_max = int(prime_max if prime_max is not None else preset.get("prime_max", 23))
        self.augment = augment

        primes = list(sp.primerange(2, self.prime_max + 1))
        chosen = [random.choice(primes) for _ in range(self.num_primes)]
        self.n = 1
        for p in chosen:
            self.n *= p
        self._factorization = sp.factorint(self.n)

        description = get_template(
            PROMPT_TEMPLATES["prime_factorization"], "problem", language,
            augment=augment, n=self.n,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _format_factorization(self) -> str:
        parts = []
        for base in sorted(self._factorization):
            exp = self._factorization[base]
            parts.append(f"{base}^{exp}" if exp > 1 else f"{base}")
        return " * ".join(parts)

    def solve(self):
        section = PROMPT_TEMPLATES["prime_factorization"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        result = self._format_factorization()
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).replace("×", "*").replace("·", "*")
        if "=" in text:  # отбрасываем возможное "N = ..." слева
            text = text.split("=")[-1]
        # Токены вида "p^k" или "p".
        product = 1
        found = False
        for m in re.finditer(r"(\d+)\s*(?:\^|\*\*)\s*(\d+)|(\d+)", text):
            if m.group(1) is not None:
                base, exp = int(m.group(1)), int(m.group(2))
            else:
                base, exp = int(m.group(3)), 1
            if base < 2 or not sp.isprime(base):
                return 0.0
            product *= base ** exp
            found = True
        if not found:
            return 0.0
        return 1.0 if product == self.n else 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "PrimeFactorizationTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
