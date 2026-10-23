"""SchroderRowTask — большие числа Шрёдера.

S(0) = 1, S(1) = 2. Дальше (n+1)*S(n) = (6*n-3)*S(n-1) - (n-2)*S(n-2). Деление целое.
Индекс растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def schroder_trace(order: int) -> Tuple[List[int], List[int]]:
    values = [1, 2]
    numerators = [0, 0]
    for index in range(2, order + 1):
        numer = (6 * index - 3) * values[-1] - (index - 2) * values[-2]
        den = index + 1
        assert numer % den == 0
        values.append(numer // den)
        numerators.append(numer)
    return values[: order + 1], numerators[: order + 1]


class SchroderRowTask(BaseMathTask):
    TASK_TYPE = "schroder_row"
    TASK_TYPES = ["value", "numer"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values, self.numerators = schroder_trace(self.n)
        self.value = self.values[-1]
        self.numer = self.numerators[-1]
        self.answer = self.value if self.task_type == "value" else self.numer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=0, value=self.values[0]),
            texts.t("s2", self.language, i=1, value=self.values[1]),
        ]
        for index in range(2, self.n + 1):
            steps.append(texts.t(
                "s3", self.language, i=index, numer=self.numerators[index],
                den=index + 1, value=self.values[index],
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
