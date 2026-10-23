"""LrDecayTask — шаг градиента с убывающим множителем.

Множитель делится пополам в конце каждого кратного шага и не падает ниже 1.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lr_trace(start: int, gradients: Sequence[int], rate: int, period: int) -> List[Tuple[int, int, int]]:
    weight = start
    trace = []
    for index, gradient in enumerate(gradients, 1):
        used = rate
        weight -= used * gradient
        if index % period == 0:
            rate = max(1, rate // 2)
        trace.append((used, weight, rate))
    return trace


class LrDecayTask(BaseMathTask):
    TASK_TYPE = "lr_decay"
    TASK_TYPES = ["weight", "rate"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "p": 2, "r": 4}, 2: {"n": 4, "p": 2, "r": 4},
        3: {"n": 5, "p": 2, "r": 4}, 4: {"n": 6, "p": 2, "r": 8},
        5: {"n": 7, "p": 3, "r": 8}, 6: {"n": 8, "p": 3, "r": 8},
        7: {"n": 9, "p": 3, "r": 8}, 8: {"n": 10, "p": 4, "r": 8},
        9: {"n": 12, "p": 4, "r": 8}, 10: {"n": 14, "p": 4, "r": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.period = max(1, int(p["p"]))
        self.rate0 = max(1, int(p["r"]))
        self.start = random.randint(-4, 4)
        self.gradients = [random.randint(-3, 3) for _ in range(self.n)]
        self.trace = lr_trace(self.start, self.gradients, self.rate0, self.period)
        _, self.weight, self.rate = self.trace[-1]
        self.answer = self.weight if self.task_type == "weight" else self.rate
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(gradient) for gradient in self.gradients)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(
            key, language, n=self.n, start=self.start, rate=self.rate0,
            period=self.period, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gradient=gradient, used=used, weight=weight, rate=rate)
            for index, (gradient, (used, weight, rate)) in enumerate(zip(self.gradients, self.trace), 1)
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
