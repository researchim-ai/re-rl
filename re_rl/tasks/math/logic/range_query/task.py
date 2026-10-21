"""RangeQueryTask — точечные замены и сумма отрезка.

Замены применяются по порядку к исходному массиву. Границы отрезка включительны.
Номера позиций с 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Update = Tuple[int, int]


def apply_updates(values: Sequence[int], updates: Sequence[Update], left: int, right: int) -> Tuple[int, int]:
    current = list(values)
    for index, value in updates:
        current[index] = value
    return sum(current[left:right + 1]), sum(current)


class RangeQueryTask(BaseMathTask):
    TASK_TYPE = "range_query"
    TASK_TYPES = ["range", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "u": 2, "mag": 6}, 2: {"n": 6, "u": 2, "mag": 8},
        3: {"n": 6, "u": 3, "mag": 8}, 4: {"n": 8, "u": 3, "mag": 10},
        5: {"n": 8, "u": 4, "mag": 10}, 6: {"n": 10, "u": 5, "mag": 12},
        7: {"n": 12, "u": 6, "mag": 12}, 8: {"n": 14, "u": 6, "mag": 15},
        9: {"n": 16, "u": 8, "mag": 15}, 10: {"n": 18, "u": 8, "mag": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.n_updates = int(p["u"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.values = [random.randint(-self.mag, self.mag) for _ in range(self.n)]
        self.updates = [
            (random.randrange(self.n), random.randint(-self.mag, self.mag))
            for _ in range(self.n_updates)
        ]
        self.left = random.randrange(self.n)
        self.right = random.randrange(self.left, self.n)
        self.range_sum, self.total = apply_updates(self.values, self.updates, self.left, self.right)
        self.answer = self.range_sum if self.task_type == "range" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown_updates(self) -> str:
        return "; ".join(f"{index + 1} = {value}" for index, value in self.updates)

    def _descr(self, language):
        data = " ".join(map(str, self.values))
        rule = ((texts.t('s0', language, data=data, v1=self._shown_updates())))
        if self.task_type == "range":
            ask = ((texts.t('s2', language, v0=self.left + 1, v1=self.right + 1)))
        else:
            ask = (((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        step = ((texts.t('s1', self.language, range_sum=self.range_sum, total=self.total)))
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
