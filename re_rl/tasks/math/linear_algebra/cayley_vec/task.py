"""CayleyVecTask — степень матрицы 2 на 2 и вектор по теореме Гамильтона–Кэли.

Следующий вектор и следующий след степени линейно выражаются через два предыдущих следом и определителем.
Число умножений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def apply_trace(a: int, b: int, c: int, d: int, x0: int, y0: int, count: int) -> List[Tuple[int, int]]:
    if count < 1:
        raise RuntimeError("power mismatch")
    trace_sum = a + d
    det = a * d - b * c
    x, y = x0, y0
    nx = a * x + b * y
    ny = c * x + d * y
    trace = [(nx, trace_sum)]
    old_x, old_y = x, y
    x, y = nx, ny
    power_old = 2
    power_prev = trace_sum
    m00, m01, m10, m11 = a, b, c, d
    for _step in range(2, count + 1):
        nx = a * x + b * y
        ny = c * x + d * y
        if nx != trace_sum * x - det * old_x or ny != trace_sum * y - det * old_y:
            raise RuntimeError("power mismatch")
        power = trace_sum * power_prev - det * power_old
        n00 = a * m00 + b * m10
        n01 = a * m01 + b * m11
        n10 = c * m00 + d * m10
        n11 = c * m01 + d * m11
        if n00 + n11 != power:
            raise RuntimeError("power mismatch")
        trace.append((nx, power))
        old_x, old_y = x, y
        x, y = nx, ny
        power_old, power_prev = power_prev, power
        m00, m01, m10, m11 = n00, n01, n10, n11
    return trace


class CayleyVecTask(BaseMathTask):
    TASK_TYPE = "cayley_vec"
    TASK_TYPES = ["coord", "power"]

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
        self.n = max(1, int(p["n"]))
        self.a = random.randint(-2, 2)
        self.b = random.randint(-2, 2)
        self.c = random.randint(-2, 2)
        self.d = random.randint(-2, 2)
        self.x0 = random.randint(-2, 2)
        self.y0 = random.randint(-2, 2)
        self.trace = apply_trace(self.a, self.b, self.c, self.d, self.x0, self.y0, self.n)
        self.coord = self.trace[-1][0]
        self.power = self.trace[-1][1]
        self.answer = self.coord if self.task_type == "coord" else self.power
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "coord" else "s1"
        return texts.t(
            key, language, n=self.n, a=self.a, b=self.b, c=self.c, d=self.d, x=self.x0, y=self.y0,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, coord=coord, power=power)
            for index, (coord, power) in enumerate(self.trace, 1)
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
