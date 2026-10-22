"""CfExpandTask — подходящие дроби цепной дроби заданной длины.

Число неполных частных растёт с уровнем. Числитель и знаменатель считаются рекуррентно, а не одной подстановкой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def convergents(quotients: List[int]) -> List[Tuple[int, int]]:
    prev_p, prev_q = 0, 1
    numer, denom = 1, 0
    pairs = []
    for quotient in quotients:
        prev_p, numer = numer, quotient * numer + prev_p
        prev_q, denom = denom, quotient * denom + prev_q
        pairs.append((numer, denom))
    return pairs


class CfExpandTask(BaseMathTask):
    TASK_TYPE = "cf_expand"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "a": 3}, 2: {"n": 2, "a": 4}, 3: {"n": 3, "a": 3},
        4: {"n": 3, "a": 4}, 5: {"n": 4, "a": 3}, 6: {"n": 5, "a": 3},
        7: {"n": 6, "a": 3}, 8: {"n": 7, "a": 2}, 9: {"n": 8, "a": 2},
        10: {"n": 10, "a": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["a"])
        self.quotients = [random.randint(1, limit) for _ in range(self.n)]
        self.pairs = convergents(self.quotients)
        self.numer, self.denom = self.pairs[-1]
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.quotients)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, a=quotient, numer=numer, denom=denom)
            for i, (quotient, (numer, denom)) in enumerate(zip(self.quotients, self.pairs), 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
