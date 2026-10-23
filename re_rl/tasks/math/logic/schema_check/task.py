"""SchemaCheckTask — запись верна, если первое поле положительно и два других различны.

Число записей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Record = Tuple[int, int, int]


def schema_trace(records: Sequence[Record]) -> List[Tuple[int, int]]:
    valid = 0
    first = 0
    trace = []
    for index, (left, mid, right) in enumerate(records, 1):
        if left > 0 and mid != right:
            valid += 1
        elif first == 0:
            first = index
        trace.append((valid, first))
    return trace


class SchemaCheckTask(BaseMathTask):
    TASK_TYPE = "schema_check"
    TASK_TYPES = ["valid", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.records = [
            (random.randint(0, 3), random.randint(0, 3), random.randint(0, 3))
            for _ in range(self.n)
        ]
        self.trace = schema_trace(self.records)
        self.valid, self.first = self.trace[-1]
        self.answer = self.valid if self.task_type == "valid" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{left} {mid} {right}" for left, mid, right in self.records)
        key = "s0" if self.task_type == "valid" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, valid=valid, first=first)
            for index, (valid, first) in enumerate(self.trace, 1)
        ]
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
