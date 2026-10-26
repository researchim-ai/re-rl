"""ZeemanLineTask — зеемановские компоненты дипольного перехода.

Магнитное число меняется на -1, 0 или 1 и не выходит за пределы своего l.
Число предложенных компонент растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Line = Tuple[int, int]


def zeeman_trace(lines: Sequence[Line], upper_l: int, lower_l: int) -> List[Tuple[int, int]]:
    allowed = 0
    total = 0
    trace = []
    for upper, lower in lines:
        if abs(upper) <= upper_l and abs(lower) <= lower_l and abs(upper - lower) <= 1:
            allowed += 1
            total += upper - lower
        trace.append((allowed, total))
    return trace


class ZeemanLineTask(BaseMathTask):
    TASK_TYPE = "zeeman_line"
    TASK_TYPES = ["allowed", "shift"]

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
        self.lower_l = random.randint(0, 3)
        self.upper_l = self.lower_l + 1
        span = self.upper_l + 2
        self.lines = [
            (random.randint(-span, span), random.randint(-span, span))
            for _ in range(self.n)
        ]
        self.trace = zeeman_trace(self.lines, self.upper_l, self.lower_l)
        self.allowed = self.trace[-1][0]
        self.shift = self.trace[-1][1]
        self.answer = self.allowed if self.task_type == "allowed" else self.shift
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{upper} {lower}" for upper, lower in self.lines)

    def _descr(self, language):
        key = "s0" if self.task_type == "allowed" else "s1"
        return texts.t(
            key, language, n=self.n, hi=self.upper_l, lo=self.lower_l, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, allowed=allowed, shift=shift)
            for index, (allowed, shift) in enumerate(self.trace, 1)
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
