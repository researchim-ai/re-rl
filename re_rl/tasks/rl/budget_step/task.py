"""BudgetStepTask — шаг по линии, пока хватает запаса.

Ноль бесплатен и оставляет место. Шаг +1 или -1 стоит единицу запаса. Если запаса нет, шаг блокируется.
Число действий растёт с уровнем, запас равен половине этого числа.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def budget_trace(budget: int, actions: Sequence[int]) -> List[Tuple[int, int, int]]:
    place = 0
    blocked = 0
    trace = []
    for action in actions:
        cost = 0 if action == 0 else 1
        if cost > budget:
            blocked += 1
        else:
            budget -= cost
            place += action
        trace.append((place, budget, blocked))
    return trace


class BudgetStepTask(BaseMathTask):
    TASK_TYPE = "budget_step"
    TASK_TYPES = ["place", "blocked"]

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
        self.budget = self.n // 2
        self.actions = [random.choice((-1, 0, 1)) for _ in range(self.n)]
        self.trace = budget_trace(self.budget, self.actions)
        self.place = self.trace[-1][0]
        self.blocked = self.trace[-1][2]
        self.answer = self.place if self.task_type == "place" else self.blocked
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(action) for action in self.actions)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, budget=self.budget, actions=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, action=action, place=place, budget=budget, blocked=blocked)
            for index, (action, (place, budget, blocked)) in enumerate(zip(self.actions, self.trace), 1)
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
