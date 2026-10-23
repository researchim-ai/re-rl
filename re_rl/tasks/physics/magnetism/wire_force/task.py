"""WireForceTask — сила на прямые участки провода в поле.

Сила участка равна току, умноженному на длину и на поле.
Число участков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Segment = Tuple[int, int, int]


def wire_trace(segments: Sequence[Segment]) -> List[Tuple[int, int, int]]:
    total = 0
    best = -1
    which = 1
    trace = []
    for index, (current, length, field) in enumerate(segments, 1):
        force = current * length * field
        total += force
        if force > best:
            best = force
            which = index
        trace.append((force, total, which))
    return trace


class WireForceTask(BaseMathTask):
    TASK_TYPE = "wire_force"
    TASK_TYPES = ["force", "segment"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.segments = [
            (random.randint(1, 4), random.randint(1, 5), random.randint(1, 4))
            for _ in range(self.n)
        ]
        self.trace = wire_trace(self.segments)
        _, self.force, self.segment = self.trace[-1]
        self.answer = self.force if self.task_type == "force" else self.segment
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{current}, {length}, {field}" for current, length, field in self.segments
        )
        key = "s0" if self.task_type == "force" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, force=force, total=total, segment=segment)
            for index, (force, total, segment) in enumerate(self.trace, 1)
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
