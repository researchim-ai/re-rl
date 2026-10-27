"""PartsWalkTask — ковариация и площадь Леви двух блужданий.

Приращение произведения равно двум левым интегралам плюс произведение приращений.
Число пар приращений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def parts_trace(x0: int, y0: int, pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    left = x0
    right = y0
    ix = 0
    iy = 0
    cov = 0
    area = 0
    trace = []
    for dx, dy in pairs:
        ix += left * dy
        iy += right * dx
        cov += dx * dy
        area += left * dy - right * dx
        left += dx
        right += dy
        if left * right - x0 * y0 != ix + iy + cov:
            raise RuntimeError("parts mismatch")
        if ix - iy != area:
            raise RuntimeError("parts mismatch")
        trace.append((cov, area))
    return trace


class PartsWalkTask(BaseMathTask):
    TASK_TYPE = "parts_walk"
    TASK_TYPES = ["cov", "area"]

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
        self.x0 = random.randint(-2, 2)
        self.y0 = random.randint(-2, 2)
        self.pairs = [
            (random.randint(-2, 2), random.randint(-2, 2)) for _ in range(self.n)
        ]
        self.trace = parts_trace(self.x0, self.y0, self.pairs)
        self.cov = self.trace[-1][0]
        self.area = self.trace[-1][1]
        self.answer = self.cov if self.task_type == "cov" else self.area
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{dx} {dy}" for dx, dy in self.pairs)

    def _descr(self, language):
        key = "s0" if self.task_type == "cov" else "s1"
        return texts.t(key, language, n=self.n, x0=self.x0, y0=self.y0, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cov=cov, area=area)
            for index, (cov, area) in enumerate(self.trace, 1)
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
