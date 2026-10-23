"""SnellShiftTask — боковой сдвиг луча в стопке слоёв.

Сдвиг слоя — инвариант, умноженный на толщину и делённый на показатель.
Число слоёв растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Layer = Tuple[int, int]


def snell_divisors(invariant: int) -> List[int]:
    return [value for value in range(1, invariant + 1) if invariant % value == 0]


def snell_trace(invariant: int, layers: Sequence[Layer]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for index_n, thickness in layers:
        shift = invariant * thickness // index_n
        total += shift
        trace.append((shift, total))
    return trace


class SnellShiftTask(BaseMathTask):
    TASK_TYPE = "snell_shift"
    TASK_TYPES = ["shift", "layer"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "k": 12}, 2: {"n": 2, "k": 12}, 3: {"n": 3, "k": 12},
        4: {"n": 4, "k": 24}, 5: {"n": 5, "k": 24}, 6: {"n": 6, "k": 36},
        7: {"n": 7, "k": 36}, 8: {"n": 8, "k": 48}, 9: {"n": 10, "k": 60},
        10: {"n": 12, "k": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.invariant = max(1, int(p["k"]))
        choices = snell_divisors(self.invariant)
        self.layers = [
            (random.choice(choices), random.randint(1, 5))
            for _ in range(self.n)
        ]
        self.trace = snell_trace(self.invariant, self.layers)
        self.k = random.randint(1, self.n)
        self.layer = self.trace[self.k - 1][0]
        self.shift = self.trace[-1][1]
        self.answer = self.shift if self.task_type == "shift" else self.layer
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{index_n}, {thickness}" for index_n, thickness in self.layers)
        key = "s0" if self.task_type == "shift" else "s1"
        return texts.t(key, language, invariant=self.invariant, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, shift=shift, total=total)
            for index, (shift, total) in enumerate(self.trace, 1)
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
