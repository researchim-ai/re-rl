"""LatenessTask — опоздание при обслуживании в заданном порядке.

Заявки не переставляются. Опоздание — насколько завершение позже срока, но не ниже нуля.
Число заявок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Job = Tuple[int, int]


def lateness_trace(jobs: Sequence[Job]) -> List[Tuple[int, int, int]]:
    done = 0
    total = 0
    late = 0
    trace = []
    for duration, deadline in jobs:
        done += duration
        over = done - deadline
        if over < 0:
            over = 0
        if over:
            late += 1
        total += over
        trace.append((done, total, late))
    return trace


class LatenessTask(BaseMathTask):
    TASK_TYPE = "lateness"
    TASK_TYPES = ["sum", "count"]

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
        self.jobs = []
        done = 0
        for _ in range(self.n):
            duration = random.randint(1, 6)
            done += duration
            deadline = random.randint(1, done + 4)
            self.jobs.append((duration, deadline))
        self.trace = lateness_trace(self.jobs)
        _, self.sum, self.count = self.trace[-1]
        self.answer = self.sum if self.task_type == "sum" else self.count
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{duration}, {deadline}" for duration, deadline in self.jobs)
        key = "s0" if self.task_type == "sum" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, done=done, total=total, late=late)
            for index, (_, (done, total, late)) in enumerate(zip(self.jobs, self.trace), 1)
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
