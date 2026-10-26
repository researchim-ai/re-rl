"""BoxJumpTask — переходы частицы в бесконечной яме.

Энергия уровня равна квадрату номера. Дипольный переход меняет номер на нечётное число.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Jump = Tuple[int, int]


def well_trace(jumps: Sequence[Jump]) -> List[Tuple[int, int]]:
    allowed = 0
    energy = 0
    trace = []
    for start, end in jumps:
        if abs(start - end) % 2 == 1:
            allowed += 1
            energy += abs(start * start - end * end)
        trace.append((allowed, energy))
    return trace


class BoxJumpTask(BaseMathTask):
    TASK_TYPE = "box_jump"
    TASK_TYPES = ["energy", "allowed"]

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
        self.jumps = [
            (random.randint(1, 6), random.randint(1, 6)) for _ in range(self.n)
        ]
        self.trace = well_trace(self.jumps)
        self.energy = self.trace[-1][1]
        self.allowed = self.trace[-1][0]
        self.answer = self.energy if self.task_type == "energy" else self.allowed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{start} {end}" for start, end in self.jumps)

    def _descr(self, language):
        key = "s0" if self.task_type == "energy" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, allowed=allowed, energy=energy)
            for index, (allowed, energy) in enumerate(self.trace, 1)
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
