"""RelayTimeTask — эстафета из нескольких участков.

Число участков растёт с уровнем. Длина каждого участка кратна скорости, поэтому время целое.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RelayTimeTask(BaseMathTask):
    TASK_TYPE = "relay_time"
    TASK_TYPES = ["total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 6, "t": 4}, 2: {"n": 2, "v": 8, "t": 5},
        3: {"n": 3, "v": 8, "t": 6}, 4: {"n": 3, "v": 10, "t": 6},
        5: {"n": 4, "v": 12, "t": 8}, 6: {"n": 5, "v": 12, "t": 8},
        7: {"n": 6, "v": 15, "t": 10}, 8: {"n": 7, "v": 16, "t": 10},
        9: {"n": 8, "v": 18, "t": 12}, 10: {"n": 10, "v": 20, "t": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "total"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.legs: List[Dict[str, int]] = []
        for _ in range(self.n):
            speed = random.randint(1, int(p["v"]))
            time = random.randint(1, int(p["t"]))
            self.legs.append({"speed": speed, "time": time, "distance": speed * time})
        self.total = sum(leg["time"] for leg in self.legs)
        self.answer = self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [
            texts.t("s1", language, i=i, distance=leg["distance"], speed=leg["speed"])
            for i, leg in enumerate(self.legs, 1)
        ]
        return texts.t("s0", language, n=self.n, legs=" ".join(parts))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, distance=leg["distance"], speed=leg["speed"], time=leg["time"])
            for i, leg in enumerate(self.legs, 1)
        ]
        steps.append(texts.t("s3", self.language, total=self.total))
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
