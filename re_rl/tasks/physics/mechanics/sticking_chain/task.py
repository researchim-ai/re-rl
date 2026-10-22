"""StickingChainTask — неупругое слипание одинаковых тележек.

Число тележек растёт с уровнем. Скорости подогнаны так, чтобы итоговая скорость была целой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class StickingChainTask(BaseMathTask):
    TASK_TYPE = "sticking_chain"
    TASK_TYPES = ["speed", "momentum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 4, "m": 4}, 2: {"n": 2, "v": 5, "m": 5},
        3: {"n": 3, "v": 6, "m": 5}, 4: {"n": 3, "v": 6, "m": 6},
        5: {"n": 4, "v": 8, "m": 6}, 6: {"n": 5, "v": 8, "m": 8},
        7: {"n": 6, "v": 10, "m": 8}, 8: {"n": 7, "v": 10, "m": 10},
        9: {"n": 8, "v": 12, "m": 10}, 10: {"n": 10, "v": 12, "m": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.mass = random.randint(1, int(p["m"]))
        limit = int(p["v"])
        self.velocities: List[int] = [random.randint(-limit, limit) for _ in range(self.n)]
        self.velocities[-1] -= sum(self.velocities) % self.n
        self.speed = sum(self.velocities) // self.n
        self.momenta = [self.mass * item for item in self.velocities]
        self.momentum = sum(self.momenta)
        self.answer = self.speed if self.task_type == "speed" else self.momentum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.velocities)
        key = "s0" if self.task_type == "speed" else "s1"
        return texts.t(key, language, n=self.n, mass=self.mass, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, mass=self.mass, velocity=velocity, momentum=momentum)
            for i, (velocity, momentum) in enumerate(zip(self.velocities, self.momenta), 1)
        ]
        steps.append(texts.t(
            "s3", self.language, momentum=self.momentum, mass=self.mass * self.n, speed=self.speed,
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
