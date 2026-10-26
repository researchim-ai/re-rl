"""HIndexTask — индекс по убывающим цитированиям.

Индекс — наибольшая позиция, у которой цитирований не меньше номера позиции.
Число статей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def h_trace(citations: Sequence[int]) -> List[Tuple[int, int]]:
    ordered = sorted(citations, reverse=True)
    index = 0
    trace = []
    for place, cites in enumerate(ordered, 1):
        if cites >= place:
            index = place
        boundary = ordered[index - 1] if index else 0
        trace.append((index, boundary))
    return trace


class HIndexTask(BaseMathTask):
    TASK_TYPE = "h_index"
    TASK_TYPES = ["index", "boundary"]

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
        self.citations = [random.randint(0, 12) for _ in range(self.n)]
        self.trace = h_trace(self.citations)
        self.index = self.trace[-1][0]
        self.boundary = self.trace[-1][1]
        self.answer = self.index if self.task_type == "index" else self.boundary
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.citations)

    def _descr(self, language):
        key = "s0" if self.task_type == "index" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, rank=rank, boundary=boundary)
            for index, (rank, boundary) in enumerate(self.trace, 1)
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
