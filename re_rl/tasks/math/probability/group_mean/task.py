"""GroupMeanTask — сумма и число наблюдений выбранной группы.

Остальные группы в условную сумму не входят.
Число наблюдений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def cond_trace(pairs: Sequence[Pair], group: int) -> List[Tuple[int, int]]:
    count = 0
    total = 0
    trace = []
    for kind, value in pairs:
        if kind == group:
            count += 1
            total += value
        trace.append((count, total))
    return trace


class GroupMeanTask(BaseMathTask):
    TASK_TYPE = "group_mean"
    TASK_TYPES = ["count", "total"]

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
        self.group = random.randint(1, 3)
        self.pairs = [(random.randint(1, 3), random.randint(1, 9)) for _ in range(self.n)]
        self.trace = cond_trace(self.pairs, self.group)
        self.count = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.count if self.task_type == "count" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{kind} {value}" for kind, value in self.pairs)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, group=self.group, pairs=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kind=kind, value=value, count=count, total=total)
            for index, ((kind, value), (count, total)) in enumerate(zip(self.pairs, self.trace), 1)
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
