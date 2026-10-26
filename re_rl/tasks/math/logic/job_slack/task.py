"""JobSlackTask — запас времени работ проекта.

Ранний срок идёт вперёд по ожиданиям, поздний срок — назад от конца проекта.
Число работ растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def slack_trace(durations: Sequence[int], preds: Sequence[int]) -> List[Tuple[int, int]]:
    count = len(durations)
    earliest = []
    finish_at = []
    for index, duration in enumerate(durations):
        start = finish_at[preds[index] - 1] if preds[index] else 0
        earliest.append(start)
        finish_at.append(start + duration)
    project = max(finish_at)
    dependents = [[] for _ in durations]
    for index, pred in enumerate(preds):
        if pred:
            dependents[pred - 1].append(index)
    latest_finish = [project] * count
    latest_start = [0] * count
    for index in range(count - 1, -1, -1):
        if dependents[index]:
            latest_finish[index] = min(latest_start[item] for item in dependents[index])
        latest_start[index] = latest_finish[index] - durations[index]
    critical = 0
    trace = []
    for index, duration in enumerate(durations):
        slack = latest_start[index] - earliest[index]
        if slack == 0:
            critical += 1
        trace.append((slack, critical))
    return trace


class JobSlackTask(BaseMathTask):
    TASK_TYPE = "job_slack"
    TASK_TYPES = ["slack", "critical"]

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
        self.durations = [random.randint(1, 6) for _ in range(self.n)]
        self.preds = [0]
        for index in range(1, self.n):
            self.preds.append(random.randint(1, index))
        self.k = random.randint(1, self.n)
        self.trace = slack_trace(self.durations, self.preds)
        self.slack = self.trace[self.k - 1][0]
        self.critical = self.trace[-1][1]
        self.answer = self.slack if self.task_type == "slack" else self.critical
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        parts = []
        for index, (duration, pred) in enumerate(zip(self.durations, self.preds), 1):
            if pred:
                parts.append(f"{index} {duration} {pred}")
            else:
                parts.append(f"{index} {duration} 0")
        return "; ".join(parts)

    def _descr(self, language):
        key = "s0" if self.task_type == "slack" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing(), k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, slack=slack, critical=critical)
            for index, (slack, critical) in enumerate(self.trace, 1)
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
