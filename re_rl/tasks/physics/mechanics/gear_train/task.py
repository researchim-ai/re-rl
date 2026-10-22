"""GearTrainTask — ряд зацепленных шестерён.

Число шестерён растёт с уровнем. У всех одно и то же произведение зубьев на частоту,
поэтому каждая следующая частота целая.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GearTrainTask(BaseMathTask):
    TASK_TYPE = "gear_train"
    TASK_TYPES = ["final_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "p": 6}, 2: {"n": 2, "p": 8}, 3: {"n": 3, "p": 12},
        4: {"n": 3, "p": 12}, 5: {"n": 4, "p": 18}, 6: {"n": 5, "p": 24},
        7: {"n": 6, "p": 30}, 8: {"n": 7, "p": 36}, 9: {"n": 8, "p": 48},
        10: {"n": 10, "p": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "final_speed"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        product = random.randint(1, int(p["p"]))
        divisors = [item for item in range(1, int(p["p"]) + 1) if product % item == 0]
        self.teeth: List[int] = [random.choice(divisors) for _ in range(self.n)]
        self.speeds: List[int] = [product // item for item in self.teeth]
        self.answer = self.speeds[-1]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{i}:{teeth}" for i, teeth in enumerate(self.teeth, 1))
        return texts.t("s0", language, n=self.n, listing=listing, rpm=self.speeds[0])

    def solve(self):
        steps = []
        for index in range(1, self.n):
            steps.append(texts.t(
                "s1", self.language, i=index + 1,
                t0=self.teeth[index - 1], w0=self.speeds[index - 1],
                t1=self.teeth[index], w1=self.speeds[index],
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
