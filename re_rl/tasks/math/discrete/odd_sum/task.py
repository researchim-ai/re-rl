"""OddSumTask — сумма первых нечётных натуральных чисел равна квадрату их количества.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class OddSumTask(BaseMathTask):
    TASK_TYPE = "odd_sum"
    TASK_TYPES = ["sum", "count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 8}, 3: {"n": 10}, 4: {"n": 12}, 5: {"n": 15},
        6: {"n": 20}, 7: {"n": 25}, 8: {"n": 30}, 9: {"n": 40}, 10: {"n": 50},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = random.randint(1, int(p["n"]))
        self.square = self.n * self.n
        self.answer = self.square if self.task_type == "sum" else self.n
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "sum":
            return texts.t("s0", language, n=self.n)
        return texts.t("s1", language, square=self.square)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = texts.t("s2", self.language, n=self.n, last=2 * self.n - 1, square=self.square)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
