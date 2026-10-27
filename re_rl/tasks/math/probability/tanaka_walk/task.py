"""TanakaWalkTask — интеграл знака и локальное время в нуле.

Для шагов 1 и минус 1 модуль позиции равен модулю старта плюс интеграл знака плюс локальное время.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def tanaka_trace(start: int, steps: Sequence[int]) -> List[Tuple[int, int]]:
    pos = start
    signed = 0
    local = 0
    trace = []
    for step in steps:
        if step != 1 and step != -1:
            raise RuntimeError("tanaka mismatch")
        if pos > 0:
            sign = 1
        elif pos < 0:
            sign = -1
        else:
            sign = 0
        signed += sign * step
        if pos == 0:
            local += 1
        pos += step
        if abs(pos) != abs(start) + signed + local:
            raise RuntimeError("tanaka mismatch")
        trace.append((signed, local))
    return trace


class TanakaWalkTask(BaseMathTask):
    TASK_TYPE = "tanaka_walk"
    TASK_TYPES = ["signed", "local"]

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
        self.start = random.randint(-2, 2)
        self.steps = [random.choice((-1, 1)) for _ in range(self.n)]
        self.trace = tanaka_trace(self.start, self.steps)
        self.signed = self.trace[-1][0]
        self.local = self.trace[-1][1]
        self.answer = self.signed if self.task_type == "signed" else self.local
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(step) for step in self.steps)

    def _descr(self, language):
        key = "s0" if self.task_type == "signed" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, signed=signed, local=local)
            for index, (signed, local) in enumerate(self.trace, 1)
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
