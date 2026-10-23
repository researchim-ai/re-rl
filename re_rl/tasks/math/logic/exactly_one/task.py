"""ExactlyOneTask — группы, в которых ровно одна единица.

В каждой группе три бита. Единица в ответе группы означает сумму битов 1.
Число групп растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def exact_trace(groups: Sequence[Sequence[int]]) -> List[Tuple[int, int]]:
    hits = 0
    trace = []
    for group in groups:
        hit = 1 if sum(group) == 1 else 0
        hits += hit
        trace.append((hit, hits))
    return trace


class ExactlyOneTask(BaseMathTask):
    TASK_TYPE = "exactly_one"
    TASK_TYPES = ["count", "hit"]

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
        self.groups = [[random.randint(0, 1) for _ in range(3)] for _ in range(self.n)]
        self.trace = exact_trace(self.groups)
        self.count = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.hit = self.trace[self.k - 1][0]
        self.answer = self.count if self.task_type == "count" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        groups = " | ".join(" ".join(str(bit) for bit in group) for group in self.groups)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, groups=groups, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, hit=hit, count=count)
            for index, (hit, count) in enumerate(self.trace, 1)
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
