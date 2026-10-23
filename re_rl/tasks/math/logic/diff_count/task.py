"""DiffCountTask — сверка двух журналов одинаковой длины.

Считаются различия и позиция первого. Если журналы совпали, первое различие равно 0.
Длина растёт с уровнем. Один проход.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def diff_trace(left: Sequence[int], right: Sequence[int]) -> List[Tuple[int, int]]:
    diffs = 0
    first = 0
    trace = []
    for index, (one, other) in enumerate(zip(left, right), 1):
        if one != other:
            diffs += 1
            if first == 0:
                first = index
        trace.append((diffs, first))
    return trace


class DiffCountTask(BaseMathTask):
    TASK_TYPE = "diff_count"
    TASK_TYPES = ["diffs", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.left = [random.randint(0, 3) for _ in range(self.n)]
        self.right = [
            value if random.randint(0, 1) == 0 else random.randint(0, 3)
            for value in self.left
        ]
        self.trace = diff_trace(self.left, self.right)
        self.diffs, self.first = self.trace[-1]
        self.answer = self.diffs if self.task_type == "diffs" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, values: Sequence[int]) -> str:
        return ", ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "diffs" else "s1"
        return texts.t(key, language, n=self.n, left=self._row(self.left), right=self._row(self.right))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, one=one, other=other, diffs=diffs, first=first)
            for index, (one, other, (diffs, first)) in enumerate(zip(self.left, self.right, self.trace), 1)
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
