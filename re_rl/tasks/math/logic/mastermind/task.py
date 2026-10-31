"""MastermindTask — дедукция скрытого кода по обратной связи.

Есть скрытый код из цифр 1..C длины L. Даны несколько догадок с подсказками:
«точных» (нужная цифра на нужном месте) и «частичных» (нужная цифра не на своём
месте). Единственность совместимого кода гарантируется перебором при генерации.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import Counter
from itertools import product
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class MastermindTask(BaseMathTask):
    TASK_TYPE = "mastermind"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 3, "C": 4}, 2: {"L": 3, "C": 5}, 3: {"L": 3, "C": 6},
        4: {"L": 4, "C": 5}, 5: {"L": 4, "C": 6}, 6: {"L": 4, "C": 6},
        7: {"L": 4, "C": 7}, 8: {"L": 5, "C": 6}, 9: {"L": 5, "C": 7},
        10: {"L": 5, "C": 8},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.L = kwargs.pop("L",preset["L"])
        self.C = kwargs.pop("C",preset["C"])
        if type(self.L) is not int or not 1 <= self.L <= 8:
            raise ValueError("invalid_length")
        if type(self.C) is not int or not 1 <= self.C <= 10 or self.C**self.L > 32768:
            raise ValueError("invalid_alphabet_or_search_space")
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _feedback(self, guess: Tuple[int, ...], secret: Tuple[int, ...]) -> Tuple[int, int]:
        exact = sum(g == s for g, s in zip(guess, secret))
        common = sum((Counter(guess) & Counter(secret)).values())
        return exact, common - exact

    def _consistent(self, code, guesses) -> bool:
        return all(self._feedback(g, code) == fb for g, fb in guesses)

    def _build(self):
        self.secret = tuple(random.randint(1, self.C) for _ in range(self.L))
        remaining = list(product(range(1,self.C+1),repeat=self.L))
        self.guesses = []
        seen = set()
        for _ in range(30):
            if len(remaining)==1:break
            guess=tuple(random.randint(1,self.C) for _ in range(self.L))
            if guess==self.secret or guess in seen:continue
            seen.add(guess)
            feedback=self._feedback(guess,self.secret)
            filtered=[code for code in remaining if self._feedback(guess,code)==feedback]
            if len(filtered)<len(remaining):
                self.guesses.append((guess,feedback));remaining=filtered
        while len(remaining)>1 and len(self.guesses)<128:
            guess=next(code for code in remaining if code!=self.secret)
            feedback=self._feedback(guess,self.secret)
            self.guesses.append((guess,feedback))
            remaining=[code for code in remaining if self._feedback(guess,code)==feedback]
        if remaining != [self.secret]:raise ValueError("generation_failed")

    def _make_description(self, language: str) -> str:
        head = ((texts.t('s0', language, L=self.L, C=self.C)))
        lines = []
        for g, (e, p) in self.guesses:
            gs = " ".join(str(d) for d in g)
            lines.append(((texts.t('s4', language, gs=gs, e=e, p=p))))
        tail = ((texts.t('s1', language)))
        return head + "\n".join(lines) + tail

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        import re
        from .solver import validate_clues,feedback
        validate_clues(self.L,self.C,self.guesses)
        text=U.clean(prediction).strip()
        if text.startswith("[") and text.endswith("]"):text=text[1:-1].strip()
        if not re.fullmatch(r"\d+(?:[ ,]+\d+)*",text):return 0.0
        try:code=tuple(int(x) for x in re.findall(r"\d+",text))
        except ValueError:return 0.0
        if len(code)!=self.L or any(not 1 <= d <= self.C for d in code):return 0.0
        return float(all(feedback(guess,code)==tuple(expected) for guess,expected in self.guesses))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
