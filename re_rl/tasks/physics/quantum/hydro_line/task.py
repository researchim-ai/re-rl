"""HydroLineTask — сумма изменений энергии уровней водорода.

Энергия уровня берётся из SymPy. Дробь сокращается после каждого перехода.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp
from sympy.physics.hydrogen import E_nl

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def line_trace(levels: Sequence[int]) -> List[Tuple[int, int]]:
    total = sp.Integer(0)
    trace = []
    for start, end in zip(levels, levels[1:]):
        total = sp.together(total + E_nl(end, 1) - E_nl(start, 1))
        numer, denom = sp.fraction(total)
        trace.append((int(numer), int(denom)))
    return trace


class HydroLineTask(BaseMathTask):
    TASK_TYPE = "hydro_line"
    TASK_TYPES = ["numer", "denom"]

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
        self.levels = [random.randint(1, 4)]
        for _ in range(self.n):
            nxt = random.randint(1, 4)
            while nxt == self.levels[-1]:
                nxt = random.randint(1, 4)
            self.levels.append(nxt)
        self.trace = line_trace(self.levels)
        self.numer = self.trace[-1][0]
        self.denom = self.trace[-1][1]
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(level) for level in self.levels)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, count=self.n + 1, levels=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, start=start, end=end, numer=numer, denom=denom)
            for index, (start, end, (numer, denom)) in enumerate(
                zip(self.levels, self.levels[1:], self.trace), 1
            )
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
