"""SimpsonPoolTask — перевес внутри групп и перевес после сложения.

Доля в группе и доля после объединения считаются разными произведениями.
Число групп растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Group = Tuple[int, int, int, int]


def simpson_trace(groups: Sequence[Group]) -> List[Tuple[int, int]]:
    local_sum = 0
    sick_a = cases_a = sick_b = cases_b = 0
    trace = []
    for success_a, total_a, success_b, total_b in groups:
        local_sum += success_a * total_b - success_b * total_a
        sick_a += success_a
        cases_a += total_a
        sick_b += success_b
        cases_b += total_b
        pooled = sick_a * cases_b - sick_b * cases_a
        trace.append((local_sum, pooled))
    return trace


class SimpsonPoolTask(BaseMathTask):
    TASK_TYPE = "simpson_pool"
    TASK_TYPES = ["local", "pooled"]

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
        self.groups = []
        for _ in range(self.n):
            total_a = random.randint(1, 8)
            total_b = random.randint(1, 8)
            self.groups.append((
                random.randint(0, total_a), total_a,
                random.randint(0, total_b), total_b,
            ))
        self.trace = simpson_trace(self.groups)
        self.local = self.trace[-1][0]
        self.pooled = self.trace[-1][1]
        self.answer = self.local if self.task_type == "local" else self.pooled
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(
            f"{success_a} {total_a} {success_b} {total_b}"
            for success_a, total_a, success_b, total_b in self.groups
        )

    def _descr(self, language):
        key = "s0" if self.task_type == "local" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, local=local, pooled=pooled)
            for index, (local, pooled) in enumerate(self.trace, 1)
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
