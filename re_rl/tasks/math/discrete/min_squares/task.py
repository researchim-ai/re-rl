"""MinSquaresTask — минимум квадратов натуральных чисел с суммой n.

Единица тоже является квадратом. Ответ — целое число слагаемых.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def min_squares(n: int) -> int:
    best = [0]
    for value in range(1, n + 1):
        count = value
        root = 1
        while root * root <= value:
            count = min(count, best[value - root * root] + 1)
            root += 1
        best.append(count)
    return best[n]


class MinSquaresTask(BaseMathTask):
    TASK_TYPE = "min_squares"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 20}, 2: {"m": 40}, 3: {"m": 60}, 4: {"m": 90}, 5: {"m": 120},
        6: {"m": 180}, 7: {"m": 250}, 8: {"m": 350}, 9: {"m": 450}, 10: {"m": 600},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "count"
        self.augment = augment
        self.n = random.randint(1, int(p["m"]))
        self.answer = min_squares(self.n)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, n=self.n)))

    def solve(self):
        step = ((texts.t('s1', self.language, n=self.n, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
