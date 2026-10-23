"""SelectionSwapsTask — число обменов в сортировке выбором.

На проходе ищется минимум хвоста. Обмен считается, только если минимум не на своём месте.
Длина массива растёт с уровнем, проходов меньше длины, каждый проход линейный.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def selection_trace(values: Sequence[int]) -> Tuple[int, List[int]]:
    items = list(values)
    swaps = 0
    picks = []
    last = len(items) - 1
    for start in range(last):
        best = start
        for cursor in range(start + 1, len(items)):
            if items[cursor] < items[best]:
                best = cursor
        picks.append(best + 1)
        if best != start:
            items[start], items[best] = items[best], items[start]
            swaps += 1
    return swaps, picks


class SelectionSwapsTask(BaseMathTask):
    TASK_TYPE = "selection_swaps"
    TASK_TYPES = ["swaps", "pick"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.values = [random.randint(1, self.n) for _ in range(self.n)]
        self.swaps, self.picks = selection_trace(self.values)
        self.k = random.randint(1, self.n - 1)
        self.pick = self.picks[self.k - 1]
        self.answer = self.swaps if self.task_type == "swaps" else self.pick
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "swaps" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pick=pick)
            for index, pick in enumerate(self.picks, 1)
        ]
        steps.append(texts.t("s3", self.language, swaps=self.swaps))
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
