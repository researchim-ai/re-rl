"""MzPortTask — цепочка делителей и фазовых пластинок.

Делитель заменяет каналы (верх, низ) на (верх+низ, верх-низ). Пластинка меняет знак одного канала.
Так считается интерференция в интерферометре Маха–Цендера. Число приборов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mz_trace(ops: Sequence[int]) -> List[Tuple[int, int]]:
    upper = 1
    lower = 0
    trace = []
    for op in ops:
        if op == 0:
            upper, lower = upper + lower, upper - lower
        elif op == 1:
            lower = -lower
        else:
            upper = -upper
        trace.append((upper, lower))
    return trace


class MzPortTask(BaseMathTask):
    TASK_TYPE = "mz_port"
    TASK_TYPES = ["upper", "lower"]

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
        self.ops = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = mz_trace(self.ops)
        self.upper = self.trace[-1][0] * self.trace[-1][0]
        self.lower = self.trace[-1][1]
        self.answer = self.upper if self.task_type == "upper" else self.lower
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(op) for op in self.ops)

    def _descr(self, language):
        key = "s0" if self.task_type == "upper" else "s1"
        return texts.t(key, language, n=self.n, ops=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, upper=upper, lower=lower)
            for index, (upper, lower) in enumerate(self.trace, 1)
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
