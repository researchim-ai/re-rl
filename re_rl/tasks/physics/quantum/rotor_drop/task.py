"""RotorDropTask — спуск жёсткого ротатора по уровням.

Энергия уровня равна уровню, умноженному на уровень плюс один. За такт испускается разность с уровнем ниже.
Разность сверяет SymPy. Число спусков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rotor_trace(start: int, ticks: int) -> List[Tuple[int, int, int]]:
    level = sp.Integer(start)
    emitted = sp.Integer(0)
    trace = []
    for _ in range(ticks):
        higher = level * (level + 1)
        lower = (level - 1) * level
        photon = higher - lower
        if photon != 2 * level:
            raise RuntimeError("photon mismatch")
        emitted += photon
        current = int(level)
        level -= 1
        trace.append((current, int(photon), int(emitted)))
    return trace


class RotorDropTask(BaseMathTask):
    TASK_TYPE = "rotor_drop"
    TASK_TYPES = ["photon", "total"]

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
        self.start = self.n + random.randint(0, 4)
        self.k = random.randint(1, self.n)
        self.trace = rotor_trace(self.start, self.n)
        self.photon = self.trace[self.k - 1][1]
        self.total = self.trace[-1][2]
        self.answer = self.photon if self.task_type == "photon" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "photon" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, k=self.k)

    def solve(self):
        steps = []
        for index, (level, photon, total) in enumerate(self.trace, 1):
            higher = level * (level + 1)
            lower = higher - photon
            steps.append(texts.t(
                "s2", self.language, i=index, level=level, high=higher, low=lower,
                photon=photon, total=total,
            ))
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
