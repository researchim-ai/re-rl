"""VoltageDividerTask — последовательная цепочка резисторов.

Число резисторов растёт с уровнем. Ток целый, поэтому каждое падение напряжения целое.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class VoltageDividerTask(BaseMathTask):
    TASK_TYPE = "voltage_divider"
    TASK_TYPES = ["total", "part"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "r": 6, "i": 4}, 2: {"n": 2, "r": 8, "i": 5},
        3: {"n": 3, "r": 8, "i": 5}, 4: {"n": 3, "r": 10, "i": 6},
        5: {"n": 4, "r": 12, "i": 6}, 6: {"n": 5, "r": 12, "i": 8},
        7: {"n": 6, "r": 15, "i": 8}, 8: {"n": 7, "r": 16, "i": 10},
        9: {"n": 8, "r": 18, "i": 10}, 10: {"n": 10, "r": 20, "i": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.resistors: List[int] = [random.randint(1, int(p["r"])) for _ in range(self.n)]
        self.current = random.randint(1, int(p["i"]))
        self.drops = [self.current * item for item in self.resistors]
        self.total_r = sum(self.resistors)
        self.total_v = sum(self.drops)
        self.k = random.randint(1, self.n)
        self.part = self.drops[self.k - 1]
        self.answer = self.total_v if self.task_type == "total" else self.part
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self, language):
        parts = [
            texts.t("s2", language, i=i, r=item)
            for i, item in enumerate(self.resistors, 1)
        ]
        return " ".join(parts)

    def _descr(self, language):
        listing = self._listing(language)
        if self.task_type == "total":
            return texts.t("s0", language, n=self.n, listing=listing, current=self.current)
        return texts.t("s1", language, n=self.n, listing=listing, total=self.total_v, k=self.k)

    def solve(self):
        steps = []
        if self.task_type == "part":
            steps.append(texts.t("s6", self.language, total_r=self.total_r))
            steps.append(texts.t(
                "s5", self.language, total_v=self.total_v, total_r=self.total_r, current=self.current,
            ))
        for index, (res, drop) in enumerate(zip(self.resistors, self.drops), 1):
            steps.append(texts.t(
                "s3", self.language, i=index, r=res, current=self.current, drop=drop,
            ))
        if self.task_type == "total":
            steps.append(texts.t("s4", self.language, total=self.total_v))
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
