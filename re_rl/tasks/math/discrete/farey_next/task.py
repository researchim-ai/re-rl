"""FareyNextTask — следующая дробь в последовательности Фарея.

Ищется дробь c/d с наибольшим знаменателем не выше порядка, для которой b*c - a*d = 1.
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def farey_trace(numer: int, denom: int, order: int) -> List[Tuple[int, int]]:
    best_c = 0
    best_d = 0
    trace = []
    for candidate in range(1, order + 1):
        if (numer * candidate + 1) % denom == 0:
            other = (numer * candidate + 1) // denom
            if candidate > best_d:
                best_c = other
                best_d = candidate
        trace.append((best_c, best_d))
    return trace


class FareyNextTask(BaseMathTask):
    TASK_TYPE = "farey_next"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.denom = random.randint(1, self.n)
        self.numer = random.randint(0, self.denom - 1)
        while math.gcd(self.numer, self.denom) != 1:
            self.numer = random.randint(0, self.denom - 1)
        self.trace = farey_trace(self.numer, self.denom, self.n)
        self.next_numer, self.next_denom = self.trace[-1]
        self.answer = self.next_numer if self.task_type == "numer" else self.next_denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, numer=self.numer, denom=self.denom, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, d=index, numer=numer, denom=denom)
            for index, (numer, denom) in enumerate(self.trace, 1)
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
