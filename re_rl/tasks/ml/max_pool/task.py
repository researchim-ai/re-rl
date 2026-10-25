"""MaxPoolTask — максимум неперекрывающихся пар.

Левое число побеждает при равенстве. Число пар растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pair_max(values: Sequence[int]) -> List[Tuple[int, int]]:
    left_wins = 0
    trace = []
    for index in range(0, len(values), 2):
        left = values[index]
        right = values[index + 1]
        if left >= right:
            left_wins += 1
            winner = left
        else:
            winner = right
        trace.append((winner, left_wins))
    return trace


class MaxPoolTask(BaseMathTask):
    TASK_TYPE = "max_pool"
    TASK_TYPES = ["total", "lefts"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values = [random.randint(0, 9) for _ in range(self.n * 2)]
        self.trace = pair_max(self.values)
        self.total = sum(item[0] for item in self.trace)
        self.lefts = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.lefts
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, values=shown)

    def solve(self):
        steps = []
        for index, (winner, lefts) in enumerate(self.trace, 1):
            left = self.values[2 * index - 2]
            right = self.values[2 * index - 1]
            steps.append(texts.t("s2", self.language, i=index, left=left, right=right, winner=winner, lefts=lefts))
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
