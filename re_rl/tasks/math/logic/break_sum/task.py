"""BreakSumTask — сумма цикла до команды выхода.

Единица в признаке выходит из цикла до прибавления этого числа. Дальнейшие числа не прибавляются.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int]


def break_trace(rows: Sequence[Row]) -> List[Tuple[int, int]]:
    total = 0
    stopped = 0
    done = False
    trace = []
    for index, (value, flag) in enumerate(rows, 1):
        if not done:
            if flag:
                done = True
                stopped = index
            else:
                total += value
        trace.append((total, stopped))
    return trace


class BreakSumTask(BaseMathTask):
    TASK_TYPE = "break_sum"
    TASK_TYPES = ["total", "stop"]

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
        self.rows = [(random.randint(0, 6), random.randint(0, 1)) for _ in range(self.n)]
        self.trace = break_trace(self.rows)
        self.total = self.trace[-1][0]
        self.stop = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.stop
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{value} {flag}" for value, flag in self.rows)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, rows=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, flag=flag, total=total, stop=stop)
            for index, ((value, flag), (total, stop)) in enumerate(zip(self.rows, self.trace), 1)
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
