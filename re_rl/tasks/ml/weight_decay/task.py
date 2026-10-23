"""WeightDecayTask — шаг с целочисленным затуханием веса.

Из веса вычитаются градиент и целая часть половины текущего веса.
Деление округляет вниз. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def decay_trace(start: int, gradients: Sequence[int]) -> List[Tuple[int, int, int]]:
    weight = start
    total = 0
    trace = []
    for gradient in gradients:
        decay = weight // 2
        weight = weight - gradient - decay
        total += decay
        trace.append((decay, weight, total))
    return trace


class WeightDecayTask(BaseMathTask):
    TASK_TYPE = "weight_decay"
    TASK_TYPES = ["weight", "decay"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 4}, 3: {"n": 4, "m": 5},
        4: {"n": 5, "m": 5}, 5: {"n": 6, "m": 6}, 6: {"n": 7, "m": 6},
        7: {"n": 8, "m": 7}, 8: {"n": 10, "m": 7}, 9: {"n": 12, "m": 8},
        10: {"n": 14, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.start = random.randint(-limit, limit)
        self.gradients = [random.randint(-limit, limit) for _ in range(self.n)]
        self.trace = decay_trace(self.start, self.gradients)
        _, self.weight, self.decay = self.trace[-1]
        self.answer = self.weight if self.task_type == "weight" else self.decay
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(gradient) for gradient in self.gradients)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gradient=gradient, decay=decay, weight=weight, total=total)
            for index, (gradient, (decay, weight, total)) in enumerate(zip(self.gradients, self.trace), 1)
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
