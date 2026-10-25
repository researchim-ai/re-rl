"""DrawOutTask — выбор шаров без возвращения.

Вынутый шар не кладут обратно. Вероятность последовательности — произведение долей, сокращённое после каждого шага.
Число тиражей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def without_trace(red: int, blue: int, draws: Sequence[int]) -> List[Tuple[int, int, int]]:
    chance = Fraction(1)
    trace = []
    for bit in draws:
        total = red + blue
        have = red if bit == 1 else blue
        chance *= Fraction(have, total) if total else Fraction(0)
        if bit == 1 and red:
            red -= 1
        elif bit == 0 and blue:
            blue -= 1
        trace.append((red, chance.numerator, chance.denominator))
    return trace


class DrawOutTask(BaseMathTask):
    TASK_TYPE = "draw_out"
    TASK_TYPES = ["numer", "left"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.red = self.n + random.randint(0, 4)
        self.blue = random.randint(1, self.n)
        self.draws = []
        red, blue = self.red, self.blue
        for _ in range(self.n):
            if random.randrange(red + blue) < red:
                self.draws.append(1)
                red -= 1
            else:
                self.draws.append(0)
                blue -= 1
        self.trace = without_trace(self.red, self.blue, self.draws)
        self.left = self.trace[-1][0]
        self.numer = self.trace[-1][1]
        self.answer = self.numer if self.task_type == "numer" else self.left
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(bit) for bit in self.draws)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, red=self.red, blue=self.blue, draws=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, left=left, numer=numer, denom=denom)
            for index, (bit, (left, numer, denom)) in enumerate(zip(self.draws, self.trace), 1)
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
