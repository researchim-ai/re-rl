"""ItoLeftTask — левый интеграл Ито и квадратичная вариация блуждания.

Квадрат позиции равен удвоенному интегралу плюс сумма квадратов приращений.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ito_trace(start: int, steps: Sequence[int]) -> List[Tuple[int, int]]:
    pos = start
    ito = 0
    quad = 0
    trace = []
    for step in steps:
        ito += pos * step
        quad += step * step
        pos += step
        if pos * pos - start * start != 2 * ito + quad:
            raise RuntimeError("ito mismatch")
        trace.append((ito, quad))
    return trace


class ItoLeftTask(BaseMathTask):
    TASK_TYPE = "ito_left"
    TASK_TYPES = ["ito", "quad"]

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
        self.steps = [random.choice((-3, -2, -1, 1, 2, 3)) for _ in range(self.n)]
        self.trace = ito_trace(self.start, self.steps)
        self.ito = self.trace[-1][0]
        self.quad = self.trace[-1][1]
        self.answer = self.ito if self.task_type == "ito" else self.quad
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(step) for step in self.steps)

    def _descr(self, language):
        key = "s0" if self.task_type == "ito" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, ito=ito, quad=quad)
            for index, (ito, quad) in enumerate(self.trace, 1)
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
