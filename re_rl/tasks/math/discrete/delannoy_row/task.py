"""DelannoyRowTask — центральные числа Деланнуа.

D(n) — сумма C(n, k)^2 * 2^k по k от 0 до n.
Порядок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def delannoy_trace(order: int) -> List[Tuple[int, int, int]]:
    running = 0
    trace = []
    for k in range(order + 1):
        coefficient = binom(order, k)
        term = coefficient * coefficient * 2 ** k
        running += term
        trace.append((coefficient, term, running))
    return trace


def delannoy_recur(order: int) -> int:
    if order == 0:
        return 1
    values = [1, 3]
    for n in range(2, order + 1):
        numer = (6 * n - 3) * values[-1] - (n - 1) * values[-2]
        assert numer % n == 0
        values.append(numer // n)
    return values[order]


class DelannoyRowTask(BaseMathTask):
    TASK_TYPE = "delannoy_row"
    TASK_TYPES = ["value", "term"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = delannoy_trace(self.n)
        self.k = random.randint(0, self.n)
        self.value = self.trace[-1][2]
        self.term = self.trace[self.k][1]
        assert self.value == delannoy_recur(self.n)
        self.answer = self.value if self.task_type == "value" else self.term
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, coefficient=coefficient, term=term, running=running)
            for index, (coefficient, term, running) in enumerate(self.trace)
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
