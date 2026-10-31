"""CryptarithmeticTask — числовые ребусы вида SEND + MORE = MONEY.

Каждой букве соответствует своя цифра (биекция), ведущие цифры ненулевые.
Задача генерируется из заведомо валидного числового равенства, а проверка
ответа выполняется по существу (валидность присваивания), а не сравнением
со «своим» решением — ребус может иметь несколько решений.
"""

from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
import string
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class CryptarithmeticTask(BaseMathTask):
    """Ребус на сложение: word_a + word_b = word_c."""

    TASK_TYPE = "cryptarithmetic"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_digits": 2},
        2: {"num_digits": 2},
        3: {"num_digits": 3},
        4: {"num_digits": 3},
        5: {"num_digits": 3},
        6: {"num_digits": 4},
        7: {"num_digits": 4},
        8: {"num_digits": 4},
        9: {"num_digits": 5},
        10: {"num_digits": 5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_digits: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_digits = num_digits if num_digits is not None else preset.get("num_digits",3)
        if type(self.num_digits) is not int or not 2 <= self.num_digits <= 6:
            raise ValueError('invalid_num_digits')
        self.augment = augment

        self._word_a, self._word_b, self._word_c, self._mapping = self._build_puzzle()

        description = get_template(
            PROMPT_TEMPLATES["cryptarithmetic"], "problem", language,
            augment=augment, a=self._word_a, b=self._word_b, c=self._word_c,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _build_puzzle(self):
        letters_pool = string.ascii_uppercase
        for _ in range(500):
            n = self.num_digits
            a = random.randint(10 ** (n - 1), 10 ** n - 1)
            b = random.randint(10 ** (n - 1), 10 ** n - 1)
            c = a + b
            digits = set(str(a) + str(b) + str(c))
            if len(digits) > 10:
                continue
            # Биекция цифра -> буква (для встречающихся цифр).
            distinct = sorted(digits, key=int)
            if len(distinct) < 2:
                continue
            chosen = random.sample(letters_pool, len(distinct))
            digit_to_letter = {d: chosen[i] for i, d in enumerate(distinct)}
            wa = "".join(digit_to_letter[d] for d in str(a))
            wb = "".join(digit_to_letter[d] for d in str(b))
            wc = "".join(digit_to_letter[d] for d in str(c))
            mapping = {letter: int(d) for d, letter in digit_to_letter.items()}
            return wa, wb, wc, mapping
        # Фолбэк: тривиальный ребус.
        raise ValueError('generation_failed')

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        section = PROMPT_TEMPLATES["cryptarithmetic"]
        if self._mapping is None:
            self.solution_steps = []
            self.final_answer = texts.t('no_solution',self.language)
            return
        mapping_str = ",".join(f"{k}={v}" for k, v in sorted(self._mapping.items()))
        self.solution_steps = [get_template(section, "step_model", self.language, augment=False)]
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, mapping=mapping_str)
        )
        self.final_answer = mapping_str

    def verify(self, prediction: str) -> float:
        """Проверяет валидность присваивания: биекция, ведущие ≠ 0 и сумма."""
        import re
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()

        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction
        parts = text.strip().split(',')
        from re_rl.tasks.math.logic.puzzle_inference import cryptarithm
        if text.strip() in (texts.t('no_solution','ru'),texts.t('no_solution','en')):
            return float(cryptarithm(self._word_a,self._word_b,self._word_c,[]) is None)
        pairs = []
        for part in parts:
            match = re.fullmatch(r"\s*([A-Za-z])\s*=\s*([0-9])\s*",part)
            if match is None:return 0.0
            pairs.append(match.groups())
        if not pairs:
            return 0.0
        assignment: Dict[str, int] = {}
        for letter, digit in pairs:
            if letter.upper() in assignment:return 0.0
            assignment[letter.upper()] = int(digit)

        letters_needed = set(self._word_a + self._word_b + self._word_c)
        if letters_needed != assignment.keys():
            return 0.0
        used = {assignment[l] for l in letters_needed}
        if len(used) != len(letters_needed):
            return 0.0  # не биекция
        # Ведущие цифры ≠ 0.
        for word in (self._word_a, self._word_b, self._word_c):
            if assignment[word[0]] == 0:
                return 0.0

        def to_num(word: str) -> int:
            val = 0
            for ch in word:
                val = val * 10 + assignment[ch]
            return val

        return 1.0 if to_num(self._word_a) + to_num(self._word_b) == to_num(self._word_c) else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "CryptarithmeticTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
