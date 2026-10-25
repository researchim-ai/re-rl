"""SwitchCaseTask — выбор первой совпавшей ветки.

Метки сравниваются со значением по порядку. Первое совпадение забирает свой результат, иначе остаётся запасной.
Число веток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Branch = Tuple[int, int]


def case_trace(value: int, rows: Sequence[Branch], default: int) -> List[Tuple[int, int]]:
    chosen = default
    taken = 0
    trace = []
    for index, (label, result) in enumerate(rows, 1):
        if taken == 0 and label == value:
            chosen = result
            taken = index
        trace.append((chosen, taken))
    return trace


class SwitchCaseTask(BaseMathTask):
    TASK_TYPE = "switch_case"
    TASK_TYPES = ["chosen", "at"]

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
        self.value = random.randint(0, 5)
        self.default = random.randint(-3, 5)
        self.rows = [(random.randint(0, 5), random.randint(-3, 6)) for _ in range(self.n)]
        self.trace = case_trace(self.value, self.rows, self.default)
        self.chosen = self.trace[-1][0]
        self.at = self.trace[-1][1]
        self.answer = self.chosen if self.task_type == "chosen" else self.at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{label} -> {result}" for label, result in self.rows)
        key = "s0" if self.task_type == "chosen" else "s1"
        return texts.t(key, language, n=self.n, value=self.value, default=self.default, rows=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, label=label, result=result, chosen=chosen, at=at)
            for index, ((label, result), (chosen, at)) in enumerate(zip(self.rows, self.trace), 1)
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
