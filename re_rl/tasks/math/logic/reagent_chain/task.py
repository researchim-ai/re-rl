"""ReagentChainTask — цепочка реакций с недостающим реагентом.

На каждом шаге реакция A и B идёт столько раз, сколько позволяет меньший запас.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def react(start_a: int, start_b: int, recipes: Sequence[Tuple[int, int]]):
    left_a = start_a
    left_b = start_b
    product = 0
    trace = []
    for need_a, need_b in recipes:
        times = min(left_a // need_a, left_b // need_b)
        left_a -= times * need_a
        left_b -= times * need_b
        product += times
        trace.append((times, left_a, left_b, product))
    return trace


class ReagentChainTask(BaseMathTask):
    TASK_TYPE = "reagent_chain"
    TASK_TYPES = ["product", "left_a"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 2}, 2: {"n": 2, "m": 3}, 3: {"n": 3, "m": 3},
        4: {"n": 3, "m": 3}, 5: {"n": 4, "m": 3}, 6: {"n": 5, "m": 3},
        7: {"n": 6, "m": 4}, 8: {"n": 7, "m": 4}, 9: {"n": 8, "m": 4},
        10: {"n": 10, "m": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.recipes = [
            (random.randint(1, limit), random.randint(1, limit)) for _ in range(self.n)
        ]
        factor = random.randint(1, 3)
        self.start_a = factor * sum(need_a for need_a, _need_b in self.recipes)
        self.start_b = factor * sum(need_b for _need_a, need_b in self.recipes)
        self.trace = react(self.start_a, self.start_b, self.recipes)
        self.product = self.trace[-1][3]
        self.left_a = self.trace[-1][1]
        self.answer = self.product if self.task_type == "product" else self.left_a
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{need_a}+{need_b}" for need_a, need_b in self.recipes)
        key = "s0" if self.task_type == "product" else "s1"
        return texts.t(
            key, language, a=self.start_a, b=self.start_b, n=self.n, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, times=times, a=left_a, b=left_b, product=product)
            for index, (times, left_a, left_b, product) in enumerate(self.trace, 1)
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
