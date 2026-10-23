"""BudgetTakeTask — агент берёт заявки по порядку, пока хватает бюджета.

Слишком дорогая заявка пропускается, следующие всё ещё рассматриваются.
Число заявок растёт с уровнем. Проход один, линейный.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def budget_take(costs: Sequence[int], budget: int) -> List[Tuple[int, int, int]]:
    left = budget
    taken = 0
    trace = []
    for cost in costs:
        flag = 1 if cost <= left else 0
        if flag:
            left -= cost
            taken += 1
        trace.append((flag, taken, left))
    return trace


class BudgetTakeTask(BaseMathTask):
    TASK_TYPE = "budget_take"
    TASK_TYPES = ["taken", "left"]

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
        self.costs = [random.randint(1, 6) for _ in range(self.n)]
        self.budget = random.randint(1, sum(self.costs))
        self.trace = budget_take(self.costs, self.budget)
        self.taken = self.trace[-1][1]
        self.left = self.trace[-1][2]
        self.answer = self.taken if self.task_type == "taken" else self.left
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(cost) for cost in self.costs)
        key = "s0" if self.task_type == "taken" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, budget=self.budget)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cost=cost, flag=flag, taken=taken, left=left)
            for index, (cost, (flag, taken, left)) in enumerate(zip(self.costs, self.trace), 1)
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
