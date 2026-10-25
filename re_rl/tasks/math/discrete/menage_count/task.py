"""MenageCountTask — числа менáжа.

Слагаемое k равно (-1)^k * 2*n*(2*n-k-1)!*(n-k)! / (k!*(2*n-2*k)!). Сумма по k от 0 до n.
Порядок не меньше 3 и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def menage_trace(order: int) -> List[Tuple[int, int]]:
    running = 0
    trace = []
    for k in range(order + 1):
        numer = 2 * order * math.factorial(2 * order - k - 1) * math.factorial(order - k)
        denom = math.factorial(k) * math.factorial(2 * order - 2 * k)
        assert numer % denom == 0
        signed = numer // denom
        if k % 2:
            signed = -signed
        running += signed
        trace.append((signed, running))
    return trace


class MenageCountTask(BaseMathTask):
    TASK_TYPE = "menage_count"
    TASK_TYPES = ["value", "term"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.trace = menage_trace(self.n)
        self.k = random.randint(0, self.n)
        self.term = self.trace[self.k][0]
        self.value = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.term
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, term=term, total=total)
            for index, (term, total) in enumerate(self.trace)
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
