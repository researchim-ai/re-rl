"""CarmichaelRowTask — функция Кармайкла и накопленный нок.

Для нечётной степени простого это функция Эйлера. Для 2^k при k не меньше 3 она вдвое меньше.
Для произведения берётся наименьшее общее кратное. Верхняя граница растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def prime_powers(number: int) -> List[Tuple[int, int]]:
    factors = []
    value = number
    factor = 2
    while factor * factor <= value:
        if value % factor == 0:
            power = 0
            while value % factor == 0:
                value //= factor
                power += 1
            factors.append((factor, power))
        factor += 1 if factor == 2 else 2
    if value > 1:
        factors.append((value, 1))
    return factors


def carmichael(number: int) -> int:
    if number <= 2:
        return 1
    value = 1
    for prime, power in prime_powers(number):
        if prime == 2 and power >= 3:
            piece = 2 ** (power - 2)
        elif prime == 2:
            piece = 1 if power == 1 else 2
        else:
            piece = (prime - 1) * prime ** (power - 1)
        value = value // math.gcd(value, piece) * piece
    return value


def carmichael_trace(limit: int) -> List[Tuple[int, int]]:
    running = 1
    trace = []
    for number in range(1, limit + 1):
        value = carmichael(number)
        running = running // math.gcd(running, value) * value
        trace.append((value, running))
    return trace


class CarmichaelRowTask(BaseMathTask):
    TASK_TYPE = "carmichael_row"
    TASK_TYPES = ["lam", "lcm"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = carmichael_trace(self.n)
        self.k = random.randint(1, self.n)
        self.lam = self.trace[self.k - 1][0]
        self.lcm = self.trace[-1][1]
        self.answer = self.lam if self.task_type == "lam" else self.lcm
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "lam" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, lam=lam, lcm=running)
            for index, (lam, running) in enumerate(self.trace, 1)
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
