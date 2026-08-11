"""MastermindTask — дедукция скрытого кода по обратной связи.

Есть скрытый код из цифр 1..C длины L. Даны несколько догадок с подсказками:
«точных» (нужная цифра на нужном месте) и «частичных» (нужная цифра не на своём
месте). Единственность совместимого кода гарантируется перебором при генерации.
"""

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
        self.L = int(preset["L"])
        self.C = int(preset["C"])
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
        all_codes = list(product(range(1, self.C + 1), repeat=self.L))
        self.guesses: List[Tuple[Tuple[int, ...], Tuple[int, int]]] = []
        for _ in range(30):
            g = tuple(random.randint(1, self.C) for _ in range(self.L))
            if g == self.secret:
                continue
            self.guesses.append((g, self._feedback(g, self.secret)))
            consistent = [c for c in all_codes if self._consistent(c, self.guesses)]
            if len(consistent) == 1:
                break
        # Финальная страховка уникальности.
        consistent = [c for c in all_codes if self._consistent(c, self.guesses)]
        if len(consistent) != 1:
            # добавляем прямые подсказки, пока не станет единственным
            for c in all_codes:
                if c != self.secret and self._consistent(c, self.guesses):
                    self.guesses.append((c, self._feedback(c, self.secret)))
                consistent = [x for x in all_codes if self._consistent(x, self.guesses)]
                if len(consistent) == 1:
                    break

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        head = (f"Загадан код из {self.L} цифр (каждая от 1 до {self.C}). Для каждой догадки указано "
                f"число «точных» (верная цифра на верном месте) и «частичных» (верная цифра не на "
                f"своём месте) совпадений.\n" if ru else
                f"A secret code of {self.L} digits (each from 1 to {self.C}). For each guess we give the "
                f"number of 'exact' (right digit, right place) and 'partial' (right digit, wrong place) "
                f"matches.\n")
        lines = []
        for g, (e, p) in self.guesses:
            gs = " ".join(str(d) for d in g)
            lines.append((f"Догадка [{gs}]: точных {e}, частичных {p}." if ru else
                          f"Guess [{gs}]: exact {e}, partial {p}."))
        tail = ("\nОпределите скрытый код (перечислите цифры)." if ru else
                "\nDetermine the secret code (list the digits).")
        return head + "\n".join(lines) + tail

    def solve(self):
        ru = self.language == "ru"
        code = " ".join(str(d) for d in self.secret)
        self.solution_steps = [
            ("Оставляем только коды, совместимые со всеми подсказками." if ru else
             "Keep only the codes consistent with every clue."),
            (f"Единственный совместимый код: {code}." if ru else
             f"The unique consistent code: {code}."),
        ]
        self.final_answer = code

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) < self.L:
            return 0.0
        return 1.0 if tuple(ints[-self.L:]) == self.secret else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
