"""AgeFlowTask — три возраста с одновременным обновлением.

Новые молодые равны зрелым плюс старым, зрелые становятся прежними молодыми, старые — прежними зрелыми.
Переход сверяет матрица SymPy. Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

import sympy as sp

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def leslie_trace(young: int, ripe: int, old: int, ticks: int) -> List[Tuple[int, int, int]]:
    update = sp.Matrix([[0, 1, 1], [1, 0, 0], [0, 1, 0]])
    state = sp.Matrix([young, ripe, old])
    y = sp.Integer(young)
    r = sp.Integer(ripe)
    o = sp.Integer(old)
    trace = []
    for _ in range(ticks):
        state = update * state
        y, r, o = r + o, y, r
        if state[0] != y or state[1] != r or state[2] != o:
            raise RuntimeError("cohort mismatch")
        trace.append((int(y), int(r), int(o)))
    return trace


class AgeFlowTask(BaseMathTask):
    TASK_TYPE = "age_flow"
    TASK_TYPES = ["young", "total"]

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
        self.young = random.randint(0, 5)
        self.ripe = random.randint(0, 5)
        self.old = random.randint(0, 5)
        if self.young + self.ripe + self.old == 0:
            self.ripe = 1
        self.trace = leslie_trace(self.young, self.ripe, self.old, self.n)
        self.final_young = self.trace[-1][0]
        self.total = sum(self.trace[-1])
        self.answer = self.final_young if self.task_type == "young" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "young" else "s1"
        return texts.t(key, language, n=self.n, young=self.young, ripe=self.ripe, old=self.old)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, young=young, ripe=ripe, old=old)
            for index, (young, ripe, old) in enumerate(self.trace, 1)
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
