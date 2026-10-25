"""SylvesterRowTask — последовательность Сильвестра.

s(0) = 2. Дальше s(n) = s(n-1)*(s(n-1)-1) + 1.
Индекс растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def sylvester_trace(order: int) -> List[int]:
    values = [2]
    for _ in range(order):
        values.append(values[-1] * (values[-1] - 1) + 1)
    return values


class SylvesterRowTask(BaseMathTask):
    TASK_TYPE = "sylvester_row"
    TASK_TYPES = ["value", "prev"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = sylvester_trace(self.n)
        self.value = self.trace[-1]
        self.prev = self.trace[-2]
        self.answer = self.value if self.task_type == "value" else self.prev
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [texts.t("s2", self.language, i=0, value=self.trace[0])]
        for index in range(1, self.n + 1):
            steps.append(texts.t(
                "s3", self.language, i=index, prev=self.trace[index - 1], value=self.trace[index],
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
