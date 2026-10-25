"""LogGrowthTask — целый шаг ограниченного роста.

Прирост равен численности, умноженной на свободные места, делённой на потолок.
Деление вниз считает SymPy. Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def growth_trace(pop: int, cap: int, ticks: int) -> List[Tuple[int, int]]:
    value = sp.Integer(pop)
    limit = sp.Integer(cap)
    grown = sp.Integer(0)
    trace = []
    for _ in range(ticks):
        step = value * (limit - value) // limit
        value += step
        grown += step
        trace.append((int(value), int(grown)))
    return trace


class LogGrowthTask(BaseMathTask):
    TASK_TYPE = "log_growth"
    TASK_TYPES = ["pop", "grown"]
    CAP = 10

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
        self.pop = random.randint(1, self.CAP - 1)
        self.trace = growth_trace(self.pop, self.CAP, self.n)
        self.final_pop = self.trace[-1][0]
        self.grown = self.trace[-1][1]
        self.answer = self.final_pop if self.task_type == "pop" else self.grown
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "pop" else "s1"
        return texts.t(key, language, n=self.n, pop=self.pop, cap=self.CAP)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pop=pop, grown=grown)
            for index, (pop, grown) in enumerate(self.trace, 1)
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
