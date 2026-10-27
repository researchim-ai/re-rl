"""StiffCoolTask — неявный Эйлер для остывания к комнате.

Новая температура входит в наклон: (1 + шаг) умножить на новую температуру равно старой плюс шаг, умноженный на комнату. Явный шаг того же размера может перескочить комнату.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stiff_trace(temp: int, room: int, steps: Sequence[int]) -> List[Tuple[int, int, int]]:
    trace = []
    for step in steps:
        if step < 1:
            raise RuntimeError("cool mismatch")
        gap = temp - room
        if gap % (1 + step) != 0:
            raise RuntimeError("cool mismatch")
        explicit = temp + step * (room - temp)
        temp = room + gap // (1 + step)
        trace.append((temp, temp - room, explicit))
    return trace


class StiffCoolTask(BaseMathTask):
    TASK_TYPE = "stiff_cool"
    TASK_TYPES = ["temp", "gap"]

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
        self.factors = [random.randint(1, 3) for _ in range(self.n)]
        gap = random.randint(1, 3)
        for factor in reversed(self.factors):
            gap *= 1 + factor
        self.room = random.randint(0, 6)
        self.start = self.room + gap
        self.trace = stiff_trace(self.start, self.room, self.factors)
        self.temp = self.trace[-1][0]
        self.gap = self.trace[-1][1]
        self.answer = self.temp if self.task_type == "temp" else self.gap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(factor) for factor in self.factors)

    def _descr(self, language):
        key = "s0" if self.task_type == "temp" else "s1"
        return texts.t(
            key, language, n=self.n, start=self.start, room=self.room, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, temp=temp, gap=gap, explicit=explicit)
            for index, (temp, gap, explicit) in enumerate(self.trace, 1)
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
