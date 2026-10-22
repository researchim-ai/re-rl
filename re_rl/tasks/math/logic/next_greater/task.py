"""NextGreaterTask — ближайшее строго большее справа.

Длина массива растёт с уровнем. Равные значения не подходят: нужно именно большее.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def next_greater(values: List[int]) -> List[int]:
    answer = [-1] * len(values)
    stack: List[int] = []
    for index, value in enumerate(values):
        while stack and values[stack[-1]] < value:
            answer[stack.pop()] = index
        stack.append(index)
    return answer


class NextGreaterTask(BaseMathTask):
    TASK_TYPE = "next_greater"
    TASK_TYPES = ["missing", "distance_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 3}, 2: {"n": 3, "v": 4}, 3: {"n": 4, "v": 5},
        4: {"n": 5, "v": 6}, 5: {"n": 6, "v": 8}, 6: {"n": 8, "v": 8},
        7: {"n": 10, "v": 10}, 8: {"n": 12, "v": 10}, 9: {"n": 14, "v": 12},
        10: {"n": 16, "v": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["v"])
        self.values = [random.randint(-limit, limit) for _ in range(self.n)]
        self.nxt = next_greater(self.values)
        self.missing = sum(1 for index in self.nxt if index < 0)
        self.distance_sum = sum(index - pos for pos, index in enumerate(self.nxt) if index >= 0)
        self.answer = self.missing if self.task_type == "missing" else self.distance_sum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.values)
        key = "s0" if self.task_type == "missing" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for pos, index in enumerate(self.nxt):
            if index < 0:
                steps.append(texts.t("s2", self.language, i=pos + 1, value=self.values[pos]))
            else:
                steps.append(texts.t(
                    "s3", self.language, i=pos + 1, value=self.values[pos],
                    j=index + 1, greater=self.values[index], dist=index - pos,
                ))
        steps.append(texts.t(
            "s4", self.language, missing=self.missing, total=self.distance_sum,
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
