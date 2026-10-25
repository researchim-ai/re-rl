"""HardAttendTask — жёсткий выбор значения по наибольшему произведению.

Запрос умножается на каждый ключ. При равенстве остаётся более ранний ключ.
Число запросов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def attend_trace(keys: Sequence[int], values: Sequence[int], queries: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    trace = []
    for query in queries:
        best_at = 0
        best = keys[0] * query
        for index, key in enumerate(keys):
            score = key * query
            if score > best:
                best = score
                best_at = index
        picked = values[best_at]
        total += picked
        trace.append((best_at + 1, picked, total))
    return trace


class HardAttendTask(BaseMathTask):
    TASK_TYPE = "hard_attend"
    TASK_TYPES = ["total", "last"]

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
        self.keys = [random.randint(-3, 3) for _ in range(3)]
        self.values = [random.randint(0, 6) for _ in range(3)]
        self.queries = [random.randint(-3, 3) for _ in range(self.n)]
        self.trace = attend_trace(self.keys, self.values, self.queries)
        self.total = self.trace[-1][2]
        self.last = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        keys = ", ".join(str(key) for key in self.keys)
        values = ", ".join(str(value) for value in self.values)
        queries = ", ".join(str(query) for query in self.queries)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, keys=keys, values=values, queries=queries)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, query=query, slot=slot, picked=picked, total=total)
            for index, (query, (slot, picked, total)) in enumerate(zip(self.queries, self.trace), 1)
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
