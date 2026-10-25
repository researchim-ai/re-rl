"""CmpBranchTask — ветвление по сравнению с порогом.

Если значение меньше порога, прибавляется левое число. Иначе прибавляется правое.
Число сравнений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int, int]


def cmp_trace(start: int, steps: Sequence[Step]) -> List[Tuple[int, int]]:
    value = start
    lows = 0
    trace = []
    for pivot, low, high in steps:
        if value < pivot:
            value += low
            lows += 1
        else:
            value += high
        trace.append((value, lows))
    return trace


class CmpBranchTask(BaseMathTask):
    TASK_TYPE = "cmp_branch"
    TASK_TYPES = ["value", "lows"]

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
        self.start = random.randint(0, 6)
        self.steps = [
            (random.randint(0, 8), random.randint(-2, 3), random.randint(-2, 3))
            for _ in range(self.n)
        ]
        self.trace = cmp_trace(self.start, self.steps)
        self.value = self.trace[-1][0]
        self.lows = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.lows
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{pivot} {low} {high}" for pivot, low, high in self.steps)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, steps=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pivot=pivot, low=low, high=high, value=value, lows=lows)
            for index, ((pivot, low, high), (value, lows)) in enumerate(zip(self.steps, self.trace), 1)
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
