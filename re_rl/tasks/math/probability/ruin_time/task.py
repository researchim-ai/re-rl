"""RuinTimeTask — среднее время до разорения или цели при равных ставках.

Разность средних времён убывает на 2, а первая разность равна цели минус 1.
Число промежуточных капиталов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ruin_trace(goal: int) -> List[Tuple[int, int]]:
    if goal < 2:
        raise RuntimeError("ruin mismatch")
    duration = 0
    total = 0
    trace = []
    for index in range(1, goal):
        duration += (goal - 1) - 2 * (index - 1)
        if duration != index * (goal - index):
            raise RuntimeError("ruin mismatch")
        total += duration
        trace.append((duration, total))
    values = [0] + [item[0] for item in trace] + [0]
    for index in range(1, goal):
        if 2 * values[index] != 2 + values[index - 1] + values[index + 1]:
            raise RuntimeError("ruin mismatch")
    if total != (goal - 1) * goal * (goal + 1) // 6:
        raise RuntimeError("ruin mismatch")
    return trace


class RuinTimeTask(BaseMathTask):
    TASK_TYPE = "ruin_time"
    TASK_TYPES = ["span", "total"]

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
        self.goal = self.n + 1
        self.start = random.randint(1, self.n)
        self.trace = ruin_trace(self.goal)
        self.span = self.trace[self.start - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.span if self.task_type == "span" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "span" else "s1"
        return texts.t(key, language, n=self.n, goal=self.goal, start=self.start)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, span=span, total=total)
            for index, (span, total) in enumerate(self.trace, 1)
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
