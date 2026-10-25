"""DoseDecayTask — уровень с дозами и выводом целой половины.

Сначала приходит доза, затем снимается целая половина уровня.
Снятие считает SymPy. Число доз растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def dose_trace(doses: Sequence[int]) -> List[Tuple[int, int]]:
    level = sp.Integer(0)
    cleared = sp.Integer(0)
    trace = []
    for dose in doses:
        level += sp.Integer(dose)
        removed = level // 2
        level -= removed
        cleared += removed
        trace.append((int(level), int(cleared)))
    return trace


class DoseDecayTask(BaseMathTask):
    TASK_TYPE = "dose_decay"
    TASK_TYPES = ["level", "cleared"]

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
        self.doses = [random.randint(0, 6) for _ in range(self.n)]
        self.trace = dose_trace(self.doses)
        self.level = self.trace[-1][0]
        self.cleared = self.trace[-1][1]
        self.answer = self.level if self.task_type == "level" else self.cleared
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "level" else "s1"
        return texts.t(key, language, n=self.n, doses=self._row(self.doses))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, level=level, cleared=cleared)
            for index, (level, cleared) in enumerate(self.trace, 1)
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
