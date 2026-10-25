"""MtfListTask — перенос запрошенного номера в начало списка.

Список начинает с номеров по возрастанию. Цена запроса — его место до переноса, считая с 0.
Число запросов равно длине списка и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mtf_trace(size: int, queries: Sequence[int]) -> List[Tuple[int, int]]:
    row = list(range(size))
    cost = 0
    trace = []
    for query in queries:
        place = row.index(query)
        cost += place
        row.pop(place)
        row.insert(0, query)
        trace.append((place, cost))
    return trace


class MtfListTask(BaseMathTask):
    TASK_TYPE = "mtf_list"
    TASK_TYPES = ["cost", "place"]

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
        self.queries = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.trace = mtf_trace(self.n, self.queries)
        self.cost = self.trace[-1][1]
        self.place = self.trace[-1][0]
        self.answer = self.cost if self.task_type == "cost" else self.place
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(query) for query in self.queries)
        key = "s0" if self.task_type == "cost" else "s1"
        return texts.t(key, language, n=self.n, queries=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, query=query, place=place, cost=cost)
            for index, (query, (place, cost)) in enumerate(zip(self.queries, self.trace), 1)
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
