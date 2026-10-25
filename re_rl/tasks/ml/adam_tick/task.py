"""AdamTickTask — два целых момента и шаг веса по первому.

Первый момент — целая половина суммы себя и градиента. Второй — целая половина суммы себя и квадрата градиента.
Вес уменьшается на первый момент. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def adam_trace(start: int, gradients: Sequence[int]) -> List[Tuple[int, int, int]]:
    weight = start
    moment = 0
    square = 0
    trace = []
    for grad in gradients:
        moment = (moment + grad) // 2
        square = (square + grad * grad) // 2
        weight -= moment
        trace.append((weight, moment, square))
    return trace


class AdamTickTask(BaseMathTask):
    TASK_TYPE = "adam_tick"
    TASK_TYPES = ["weight", "moment"]

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
        self.start = random.randint(-3, 3)
        self.gradients = [random.randint(-3, 4) for _ in range(self.n)]
        self.trace = adam_trace(self.start, self.gradients)
        self.weight = self.trace[-1][0]
        self.moment = self.trace[-1][1]
        self.answer = self.weight if self.task_type == "weight" else self.moment
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(grad) for grad in self.gradients)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, gradients=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, grad=grad, weight=weight, moment=moment, square=square)
            for index, (grad, (weight, moment, square)) in enumerate(zip(self.gradients, self.trace), 1)
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
