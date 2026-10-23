"""GratingOrderTask — старший порядок дифракции для каждой длины волны.

Порядок m годится, пока m, умноженное на длину волны, не больше периода решётки.
Число длин волн растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def grating_trace(spacing: int, waves: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for wave in waves:
        orders = spacing // wave
        total += orders
        trace.append((orders, total))
    return trace


class GratingOrderTask(BaseMathTask):
    TASK_TYPE = "grating_order"
    TASK_TYPES = ["orders", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "d": 12}, 2: {"n": 3, "d": 12}, 3: {"n": 4, "d": 18},
        4: {"n": 5, "d": 24}, 5: {"n": 6, "d": 24}, 6: {"n": 7, "d": 30},
        7: {"n": 8, "d": 36}, 8: {"n": 10, "d": 36}, 9: {"n": 12, "d": 48},
        10: {"n": 14, "d": 60},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.spacing = max(1, int(p["d"]))
        self.waves = [random.randint(1, self.spacing + 2) for _ in range(self.n)]
        self.trace = grating_trace(self.spacing, self.waves)
        self.k = random.randint(1, self.n)
        self.orders = self.trace[self.k - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.orders if self.task_type == "orders" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(wave) for wave in self.waves)
        key = "s0" if self.task_type == "orders" else "s1"
        return texts.t(key, language, spacing=self.spacing, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, wave=wave, orders=orders, total=total)
            for index, (wave, (orders, total)) in enumerate(zip(self.waves, self.trace), 1)
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
