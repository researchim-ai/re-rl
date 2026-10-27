"""SnellPutTask — оболочка Снелла пута на биномиальном дереве.

Значение узла — максимум из платежа, умноженного на степень четырёх, и суммы двух потомков.
Число шагов дерева растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def envelope_trace(width: int, strike: int) -> List[Tuple[int, int, int]]:
    if width < 1 or strike < 0:
        raise RuntimeError("envelope mismatch")
    leaves = []
    for ups in range(width + 1):
        pos = 2 * ups - width
        leaves.append(strike - pos if pos < strike else 0)
    child = leaves
    trace = []
    for time in range(width - 1, -1, -1):
        factor = 4 ** (width - time)
        layer = []
        for ups in range(time + 1):
            pos = 2 * ups - time
            payoff = strike - pos if pos < strike else 0
            exercise = payoff * factor
            cont = child[ups] + child[ups + 1]
            value = exercise if exercise >= cont else cont
            layer.append(value)
            trace.append((exercise, cont, value))
        child = layer
    total = 0
    comb = 1
    for ups, payoff in enumerate(leaves):
        total += comb * payoff
        if ups < width:
            comb = comb * (width - ups) // (ups + 1)
    if len(child) != 1 or child[0] < total or trace[-1][2] != child[0]:
        raise RuntimeError("envelope mismatch")
    return trace


class SnellPutTask(BaseMathTask):
    TASK_TYPE = "snell_put"
    TASK_TYPES = ["price", "hits"]

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
        self.strike = random.randint(0, self.n)
        self.trace = envelope_trace(self.n, self.strike)
        self.price = self.trace[-1][2]
        self.hits = sum(exercise > cont for exercise, cont, _value in self.trace)
        self.answer = self.price if self.task_type == "price" else self.hits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "price" else "s1"
        return texts.t(key, language, n=self.n, strike=self.strike)

    def solve(self):
        steps = []
        index = 0
        for time in range(self.n - 1, -1, -1):
            for ups in range(time + 1):
                exercise, cont, value = self.trace[index]
                index += 1
                steps.append(texts.t(
                    "s2", self.language, t=time, j=ups, ex=exercise, cont=cont, value=value,
                ))
        if index != len(self.trace):
            raise RuntimeError("envelope mismatch")
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
