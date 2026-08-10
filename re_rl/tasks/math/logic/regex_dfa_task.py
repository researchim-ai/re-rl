"""RegexDFATask — принадлежность строки формальному языку над алфавитом {a, b}.

Язык задаётся человекочитаемым описанием (и эквивалентным регулярным выражением).
Нужно определить, принадлежит ли данная строка языку (ответ YES/NO). Проверка
эталона выполняется через ``re.fullmatch``, поэтому задача полностью верифицируема.
"""

import random
import re
from typing import Any, Callable, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


def _rand_ab(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("ab") for _ in range(n))


# Каждый шаблон: regex (для проверки) + описания + генератор заведомо
# принадлежащей языку строки (sample).
LANGUAGE_TEMPLATES: List[Dict[str, Any]] = [
    {
        "pattern": r"a*b*",
        "ru": "любое число символов 'a' (возможно ноль), за которыми идёт любое число 'b'",
        "en": "any number of 'a' (possibly zero) followed by any number of 'b'",
        "sample": lambda rng, n: "a" * rng.randint(0, n) + "b" * rng.randint(0, n),
    },
    {
        "pattern": r"(ab)*",
        "ru": "повторение блока 'ab' ноль или более раз",
        "en": "the block 'ab' repeated zero or more times",
        "sample": lambda rng, n: "ab" * rng.randint(0, max(1, n // 2)),
    },
    {
        "pattern": r"([ab][ab])*",
        "ru": "строки чётной длины (включая пустую)",
        "en": "strings of even length (including the empty string)",
        "sample": lambda rng, n: _rand_ab(rng, 2 * rng.randint(0, max(1, n // 2))),
    },
    {
        "pattern": r"[ab]*aa[ab]*",
        "ru": "строки, содержащие подстроку 'aa'",
        "en": "strings containing the substring 'aa'",
        "sample": lambda rng, n: _rand_ab(rng, rng.randint(0, n)) + "aa" + _rand_ab(rng, rng.randint(0, n)),
    },
    {
        "pattern": r"a[ab]*b",
        "ru": "строки, начинающиеся на 'a' и заканчивающиеся на 'b'",
        "en": "strings that start with 'a' and end with 'b'",
        "sample": lambda rng, n: "a" + _rand_ab(rng, rng.randint(0, n)) + "b",
    },
    {
        "pattern": r"b*a b*a b*|b*",  # чётное число символов 'a' — упрощённо до 0 или 2
        "ru": "строки, содержащие ровно ноль или два символа 'a'",
        "en": "strings containing exactly zero or two 'a' characters",
        "sample": lambda rng, n: (lambda k: "b" * rng.randint(0, n) if k == 0 else
                                  "b" * rng.randint(0, n) + "a" + "b" * rng.randint(0, n) + "a" + "b" * rng.randint(0, n))(rng.choice([0, 2])),
    },
]


class RegexDFATask(BaseMathTask):
    """Принадлежит ли строка регулярному языку над {a, b} (ответ YES/NO)."""

    TASK_TYPE = "regex_dfa"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_len": 4},
        2: {"max_len": 5},
        3: {"max_len": 6},
        4: {"max_len": 7},
        5: {"max_len": 8},
        6: {"max_len": 9},
        7: {"max_len": 10},
        8: {"max_len": 12},
        9: {"max_len": 14},
        10: {"max_len": 16},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        max_len: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.max_len = int(max_len if max_len is not None else preset.get("max_len", 8))
        self.augment = augment

        self._template = random.choice(LANGUAGE_TEMPLATES)
        self._pattern = self._template["pattern"].replace(" ", "")
        self._desc = self._template["ru"] if language == "ru" else self._template["en"]
        self._string = self._make_string()
        self._matches = re.fullmatch(self._pattern, self._string) is not None

        description = get_template(
            PROMPT_TEMPLATES["regex_dfa"], "problem", language,
            augment=augment, desc=self._desc, string=self._string or "ε",
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _make_string(self) -> str:
        rng = random
        want_match = rng.random() < 0.5
        if want_match:
            for _ in range(50):
                s = self._template["sample"](rng, self.max_len)
                if len(s) <= self.max_len and re.fullmatch(self._pattern, s):
                    return s
        # Ищем строку, НЕ принадлежащую языку.
        for _ in range(100):
            s = _rand_ab(rng, rng.randint(1, self.max_len))
            if not re.fullmatch(self._pattern, s):
                return s
        # Фолбэк: заведомо принадлежащая строка.
        s = self._template["sample"](rng, self.max_len)
        return s[: self.max_len]

    def solve(self):
        section = PROMPT_TEMPLATES["regex_dfa"]
        answer = "YES" if self._matches else "NO"
        self.solution_steps.append(
            get_template(section, "step_check", self.language, augment=False, pattern=self._pattern)
        )
        verdict = ("принадлежит" if self._matches else "не принадлежит") if self.language == "ru" \
            else ("belongs to" if self._matches else "does not belong to")
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, verdict=verdict, answer=answer)
        )
        self.final_answer = answer

    def verify(self, prediction: str) -> float:
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip().lower().strip(".!? ")
        yes = {"yes", "да", "true", "y", "1", "принадлежит", "belongs"}
        no = {"no", "нет", "false", "n", "0", "не принадлежит"}
        pred = None
        if text in yes:
            pred = "YES"
        elif text in no:
            pred = "NO"
        elif re.search(r"\b(no|нет|false|не\s+принадлеж\w*)\b", text):
            pred = "NO"
        elif re.search(r"\b(yes|да|true|принадлеж\w*|belongs?)\b", text):
            pred = "YES"
        if pred is None:
            return 0.0
        return 1.0 if pred == self.final_answer else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "RegexDFATask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
