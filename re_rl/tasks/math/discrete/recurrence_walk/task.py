"""RecurrenceWalkTask — несколько шагов рекуррентности x_k = x_{k-1} + x_{k-2}.

Число вычисляемых членов растёт с уровнем. Каждый новый член — отдельный шаг.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RecurrenceWalkTask(BaseMathTask):
    TASK_TYPE = "recurrence_walk"
    TASK_TYPES = ["last"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "a": 6}, 2: {"n": 2, "a": 8}, 3: {"n": 3, "a": 8},
        4: {"n": 3, "a": 10}, 5: {"n": 4, "a": 10}, 6: {"n": 5, "a": 12},
        7: {"n": 6, "a": 12}, 8: {"n": 7, "a": 12}, 9: {"n": 8, "a": 15},
        10: {"n": 10, "a": 15},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "last"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["a"])
        self.first = random.randint(0, limit)
        self.second = random.randint(0, limit)
        self.terms: List[int] = [self.first, self.second]
        for _ in range(self.n):
            self.terms.append(self.terms[-1] + self.terms[-2])
        self.answer = self.terms[-1]
        self.index = len(self.terms)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return texts.t("s0", language, first=self.first, second=self.second, index=self.index)

    def solve(self):
        steps = []
        for index in range(2, len(self.terms)):
            steps.append(texts.t(
                "s1", self.language, i=index + 1,
                prev=self.terms[index - 1], older=self.terms[index - 2], value=self.terms[index],
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
