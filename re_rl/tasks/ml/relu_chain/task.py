"""ReluChainTask — цепь линейных слоёв с отсечением отрицательных.

Положительный вход проходит дальше и домножает множитель на вес. Неположительный обнуляет и выход, и множитель навсегда.
Число слоёв растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Layer = Tuple[int, int]


def relu_trace(start: int, layers: Sequence[Layer]) -> List[Tuple[int, int, int]]:
    value = start
    factor = 1
    trace = []
    for weight, bias in layers:
        pre = weight * value + bias
        if pre <= 0:
            factor = 0
            value = 0
        else:
            factor *= weight
            value = pre
        trace.append((pre, value, factor))
    return trace


class ReluChainTask(BaseMathTask):
    TASK_TYPE = "relu_chain"
    TASK_TYPES = ["final", "factor"]

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
        self.start = random.randint(0, 5)
        self.layers = [
            (random.choice((-1, 0, 1)), random.randint(-2, 2))
            for _ in range(self.n)
        ]
        self.trace = relu_trace(self.start, self.layers)
        self.final = self.trace[-1][1]
        self.factor = self.trace[-1][2]
        self.answer = self.final if self.task_type == "final" else self.factor
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{weight} {bias}" for weight, bias in self.layers)
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, layers=shown)

    def solve(self):
        steps = []
        for index, ((weight, bias), (pre, value, factor)) in enumerate(zip(self.layers, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, weight=weight, bias=bias,
                pre=pre, value=value, factor=factor,
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
