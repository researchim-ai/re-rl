"""CascadeTanksTask — вода переливается в следующий бак только после заполнения текущего.

Число баков растёт с уровнем. Долю в дальнем баке нельзя узнать, не пройдя предыдущие.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class CascadeTanksTask(BaseMathTask):
    TASK_TYPE = "cascade_tanks"
    TASK_TYPES = ["spilled", "tank"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "c": 5, "p": 8}, 2: {"n": 2, "c": 6, "p": 10},
        3: {"n": 3, "c": 6, "p": 12}, 4: {"n": 3, "c": 7, "p": 14},
        5: {"n": 4, "c": 7, "p": 16}, 6: {"n": 5, "c": 8, "p": 20},
        7: {"n": 6, "c": 8, "p": 24}, 8: {"n": 7, "c": 9, "p": 28},
        9: {"n": 8, "c": 9, "p": 32}, 10: {"n": 10, "c": 10, "p": 40},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.caps: List[int] = [random.randint(1, int(p["c"])) for _ in range(self.n)]
        self.pour = random.randint(1, int(p["p"]))
        self.held: List[int] = []
        left = self.pour
        for cap in self.caps:
            take = min(cap, left)
            self.held.append(take)
            left -= take
        self.spilled = left
        self.k = random.randint(1, self.n)
        self.answer = self.spilled if self.task_type == "spilled" else self.held[self.k - 1]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [texts.t("s2", language, i=i, cap=cap) for i, cap in enumerate(self.caps, 1)]
        key = "s0" if self.task_type == "spilled" else "s1"
        return texts.t(key, language, n=self.n, pour=self.pour, listing=" ".join(parts), k=self.k)

    def solve(self):
        steps = []
        left = self.pour
        for index, (cap, take) in enumerate(zip(self.caps, self.held), 1):
            left -= take
            steps.append(texts.t("s3", self.language, i=index, cap=cap, take=take, left=left))
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
