"""FillForwardTask — заполнение нулей последним ненулевым числом.

Ноль до первого ненулевого остаётся нулём. Дальше ноль заменяется последним ненулевым.
Число значений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fill_trace(values: Sequence[int]) -> List[Tuple[int, int, int]]:
    last = 0
    replaced = 0
    total = 0
    trace = []
    for value in values:
        if value == 0:
            out = last
            if last != 0:
                replaced += 1
        else:
            last = value
            out = value
        total += out
        trace.append((out, total, replaced))
    return trace


class FillForwardTask(BaseMathTask):
    TASK_TYPE = "fill_forward"
    TASK_TYPES = ["total", "replaced"]

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
        self.values = [0 if random.random() < 0.4 else random.randint(1, 6) for _ in range(self.n)]
        self.trace = fill_trace(self.values)
        self.total = self.trace[-1][1]
        self.replaced = self.trace[-1][2]
        self.answer = self.total if self.task_type == "total" else self.replaced
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, values=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, out=out, total=total, replaced=replaced)
            for index, (value, (out, total, replaced)) in enumerate(zip(self.values, self.trace), 1)
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
