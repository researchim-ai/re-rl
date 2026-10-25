"""LcTickTask — целые такты колебательного контура.

Сначала ток прибавляет напряжение, затем напряжение теряет уже новый ток.
Счёт идёт целыми числами SymPy. Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def coil_trace(voltage: int, current: int, ticks: int) -> List[Tuple[int, int]]:
    volts = sp.Integer(voltage)
    amps = sp.Integer(current)
    trace = []
    for _ in range(ticks):
        amps += volts
        volts -= amps
        trace.append((int(amps), int(volts)))
    return trace


class LcTickTask(BaseMathTask):
    TASK_TYPE = "lc_tick"
    TASK_TYPES = ["current", "voltage"]

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
        self.voltage = random.randint(-4, 4)
        self.current = random.randint(-2, 2)
        self.trace = coil_trace(self.voltage, self.current, self.n)
        self.final_current = self.trace[-1][0]
        self.final_voltage = self.trace[-1][1]
        self.answer = self.final_current if self.task_type == "current" else self.final_voltage
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "current" else "s1"
        return texts.t(key, language, n=self.n, voltage=self.voltage, current=self.current)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, current=current, voltage=voltage)
            for index, (current, voltage) in enumerate(self.trace, 1)
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
