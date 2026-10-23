"""MotionSegmentsTask — разгон и торможение по участкам.

На участке ускорение постоянно. Время чётное, поэтому скорость и координата целые.
Число участков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Segment = Tuple[int, int]


def integrate_motion(segments: Sequence[Segment]) -> List[Tuple[int, int]]:
    position = 0
    speed = 0
    trace = []
    for accel, duration in segments:
        position += speed * duration + accel * duration * duration // 2
        speed += accel * duration
        trace.append((position, speed))
    return trace


class MotionSegmentsTask(BaseMathTask):
    TASK_TYPE = "motion_segments"
    TASK_TYPES = ["place", "speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "a": 2}, 2: {"n": 2, "a": 3}, 3: {"n": 3, "a": 3},
        4: {"n": 3, "a": 4}, 5: {"n": 4, "a": 4}, 6: {"n": 5, "a": 4},
        7: {"n": 6, "a": 5}, 8: {"n": 7, "a": 5}, 9: {"n": 8, "a": 5},
        10: {"n": 10, "a": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["a"]))
        self.segments = []
        for _ in range(self.n):
            accel = random.randint(-limit, limit)
            if accel == 0:
                accel = 1
            duration = random.choice((2, 4))
            self.segments.append((accel, duration))
        self.trace = integrate_motion(self.segments)
        self.place, self.speed = self.trace[-1]
        self.answer = self.place if self.task_type == "place" else self.speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{accel}, {duration}" for accel, duration in self.segments)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, accel=accel, duration=duration, place=place, speed=speed)
            for index, ((accel, duration), (place, speed)) in enumerate(zip(self.segments, self.trace), 1)
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
