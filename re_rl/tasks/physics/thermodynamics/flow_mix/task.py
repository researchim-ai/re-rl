"""FlowMixTask — прямоточный теплообмен целыми ступенями.

На ступени целая треть разности переходит от горячего потока к холодному.
Счёт идёт целыми числами SymPy. Число ступеней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def flow_trace(hot: int, cold: int, stages: int, divisor: int = 3) -> List[Tuple[int, int]]:
    warm = sp.Integer(hot)
    cool = sp.Integer(cold)
    moved = sp.Integer(0)
    trace = []
    for _ in range(stages):
        share = (warm - cool) // divisor
        warm -= share
        cool += share
        moved += share
        trace.append((int(warm), int(moved)))
    return trace


class FlowMixTask(BaseMathTask):
    TASK_TYPE = "flow_mix"
    TASK_TYPES = ["hot", "moved"]
    DIVISOR = 3

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
        self.hot = random.randint(6, 20)
        self.cold = random.randint(0, 5)
        self.trace = flow_trace(self.hot, self.cold, self.n, self.DIVISOR)
        self.final_hot = self.trace[-1][0]
        self.moved = self.trace[-1][1]
        self.answer = self.final_hot if self.task_type == "hot" else self.moved
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "hot" else "s1"
        return texts.t(
            key, language, n=self.n, hot=self.hot, cold=self.cold, divisor=self.DIVISOR,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, hot=hot, moved=moved)
            for index, (hot, moved) in enumerate(self.trace, 1)
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
