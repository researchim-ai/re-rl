"""RoughSetTask — нижнее и верхнее приближение решения.

Два бинарных признака задают классы неразличимости. Множество — объекты с решением 1.
Нижнее приближение требует, чтобы весь класс лежал в множестве. Верхнее — чтобы класс его касался.
Число объектов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int, int]


def rough_trace(rows: Sequence[Row]) -> List[Tuple[int, int, int, int]]:
    classes: Dict[Tuple[int, int], List[int]] = {}
    for index, (left, right, _decision) in enumerate(rows):
        classes.setdefault((left, right), []).append(index)
    full = {}
    touch = {}
    for key, indexes in classes.items():
        positives = sum(rows[index][2] for index in indexes)
        full[key] = 1 if positives == len(indexes) else 0
        touch[key] = 1 if positives else 0
    lower = 0
    upper = 0
    trace = []
    for left, right, _decision in rows:
        in_lower = full[(left, right)]
        in_upper = touch[(left, right)]
        lower += in_lower
        upper += in_upper
        trace.append((in_lower, in_upper, lower, upper))
    return trace


class RoughSetTask(BaseMathTask):
    TASK_TYPE = "rough_set"
    TASK_TYPES = ["lower", "upper"]

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
        self.rows = [
            (random.randint(0, 1), random.randint(0, 1), random.randint(0, 1))
            for _ in range(self.n)
        ]
        self.trace = rough_trace(self.rows)
        self.lower = self.trace[-1][2]
        self.upper = self.trace[-1][3]
        assert self.lower <= self.upper
        self.answer = self.lower if self.task_type == "lower" else self.upper
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{left} {right} {decision}" for left, right, decision in self.rows)
        key = "s0" if self.task_type == "lower" else "s1"
        return texts.t(key, language, n=self.n, rows=shown)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, a=left, b=right, d=decision,
                low=low, up=up, lower=lower, upper=upper,
            )
            for index, ((left, right, decision), (low, up, lower, upper)) in enumerate(
                zip(self.rows, self.trace), 1
            )
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
