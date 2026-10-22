"""ExtendedEuclidTask — коэффициенты Безу за ровно n делений.

Пара строится с конца: каждое частное не меньше 1, поэтому длина цепочки фиксирована уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pair_with_steps(steps: int, scale: int, quot_max: int) -> Tuple[int, int]:
    remainder = scale
    previous = 0
    for _ in range(steps):
        quotient = random.randint(1, quot_max)
        earlier = quotient * remainder + previous
        previous, remainder = remainder, earlier
    return remainder, previous


def extended_euclid(a: int, b: int) -> Tuple[int, int, int, List[Tuple[int, int, int, int]]]:
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    trace = []
    while r:
        quotient = old_r // r
        new_r = old_r - quotient * r
        trace.append((old_r, r, quotient, new_r))
        old_r, r = r, new_r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t, trace


class ExtendedEuclidTask(BaseMathTask):
    TASK_TYPE = "extended_euclid"
    TASK_TYPES = ["x", "y"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "g": 2, "q": 2}, 2: {"n": 2, "g": 3, "q": 2},
        3: {"n": 3, "g": 3, "q": 3}, 4: {"n": 3, "g": 4, "q": 3},
        5: {"n": 4, "g": 4, "q": 3}, 6: {"n": 5, "g": 4, "q": 3},
        7: {"n": 6, "g": 5, "q": 3}, 8: {"n": 7, "g": 5, "q": 4},
        9: {"n": 8, "g": 5, "q": 4}, 10: {"n": 10, "g": 6, "q": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        scale = random.randint(1, int(p["g"]))
        self.a, self.b = pair_with_steps(self.n, scale, int(p["q"]))
        self.gcd, self.x, self.y, self.trace = extended_euclid(self.a, self.b)
        self.answer = self.x if self.task_type == "x" else self.y
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "x" else "s1"
        return texts.t(key, language, a=self.a, b=self.b)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, a=a, b=b, q=q, r=r)
            for i, (a, b, q, r) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, a=self.a, x=self.x, b=self.b, y=self.y, gcd=self.gcd))
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
