"""RenewAgeTask — число восстановлений и возраст к горизонту.

Промежутки складываются, пока сумма не станет больше горизонта. Возраст — горизонт минус сумма уложившихся промежутков.
Число промежутков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def renew_trace(intervals: Sequence[int], horizon: int) -> List[Tuple[int, int]]:
    if horizon < 0:
        raise RuntimeError("renew mismatch")
    clock = 0
    count = 0
    age = horizon
    crossed = False
    trace = []
    for span in intervals:
        if span <= 0:
            raise RuntimeError("renew mismatch")
        if not crossed:
            if clock + span <= horizon:
                clock += span
                count += 1
                age = horizon - clock
            else:
                age = horizon - clock
                residual = clock + span - horizon
                if residual <= 0 or age + residual != span:
                    raise RuntimeError("renew mismatch")
                crossed = True
        trace.append((count, age))
    if not crossed and age != horizon - clock:
        raise RuntimeError("renew mismatch")
    if count > 0:
        covered = sum(intervals[:count])
        if covered + age != horizon and crossed:
            raise RuntimeError("renew mismatch")
        if not crossed and covered != clock:
            raise RuntimeError("renew mismatch")
    return trace


class RenewAgeTask(BaseMathTask):
    TASK_TYPE = "renew_age"
    TASK_TYPES = ["count", "age"]

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
        self.intervals = [random.randint(1, 6) for _ in range(self.n)]
        total = sum(self.intervals)
        self.horizon = random.randint(0, total - 1)
        self.trace = renew_trace(self.intervals, self.horizon)
        self.count = self.trace[-1][0]
        self.age = self.trace[-1][1]
        self.answer = self.count if self.task_type == "count" else self.age
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(span) for span in self.intervals)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, horizon=self.horizon, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, count=count, age=age)
            for index, (count, age) in enumerate(self.trace, 1)
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
