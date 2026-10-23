"""TransportCostTask — цена перевозки между двумя наборами одной длины.

Оба набора упорядочивают по возрастанию, затем складывают модули разностей.
Длина наборов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def transport_trace(left: Sequence[int], right: Sequence[int]) -> List[int]:
    return [abs(first - second) for first, second in zip(sorted(left), sorted(right))]


class TransportCostTask(BaseMathTask):
    TASK_TYPE = "transport_cost"
    TASK_TYPES = ["cost", "gap"]

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
        self.left = [random.randint(0, 9) for _ in range(self.n)]
        self.right = [random.randint(0, 9) for _ in range(self.n)]
        self.trace = transport_trace(self.left, self.right)
        self.k = random.randint(1, self.n)
        self.cost = sum(self.trace)
        self.gap = self.trace[self.k - 1]
        self.answer = self.cost if self.task_type == "cost" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        left = ", ".join(str(value) for value in self.left)
        right = ", ".join(str(value) for value in self.right)
        key = "s0" if self.task_type == "cost" else "s1"
        return texts.t(key, language, n=self.n, left=left, right=right, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gap=gap)
            for index, gap in enumerate(self.trace, 1)
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
