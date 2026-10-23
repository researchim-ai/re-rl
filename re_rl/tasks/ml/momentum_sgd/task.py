"""MomentumSgdTask — шаг импульса с целочисленным затуханием.

Скорость делится пополам с округлением вниз и прибавляет градиент.
Вес затем уменьшается на скорость. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def momentum_steps(start: int, gradients: Sequence[int]) -> Tuple[List[int], List[int]]:
    weight = start
    velocity = 0
    weights = []
    velocities = []
    for gradient in gradients:
        velocity = velocity // 2 + gradient
        weight -= velocity
        weights.append(weight)
        velocities.append(velocity)
    return weights, velocities


class MomentumSgdTask(BaseMathTask):
    TASK_TYPE = "momentum_sgd"
    TASK_TYPES = ["weight", "velocity"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 4}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 5}, 8: {"n": 7, "m": 6}, 9: {"n": 8, "m": 6},
        10: {"n": 10, "m": 6},
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
        self.weights, self.velocities = momentum_steps(self.start, self.gradients)
        self.weight = self.weights[-1]
        self.velocity = self.velocities[-1]
        self.answer = self.weight if self.task_type == "weight" else self.velocity
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(gradient) for gradient in self.gradients)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gradient=gradient, velocity=velocity, weight=weight)
            for index, (gradient, velocity, weight) in enumerate(
                zip(self.gradients, self.velocities, self.weights), 1,
            )
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
