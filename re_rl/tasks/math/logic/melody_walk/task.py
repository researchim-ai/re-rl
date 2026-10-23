"""MelodyWalkTask — высота мелодии после цепочки интервалов.

Каждый интервал прибавляется к текущей высоте. Знак показывает направление.
Число интервалов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

INTERVALS = (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)


def walk_melody(start: int, intervals: Sequence[int]) -> Tuple[List[int], int]:
    pitch = start
    peak = start
    trace = []
    for interval in intervals:
        pitch += interval
        peak = max(peak, pitch)
        trace.append(pitch)
    return trace, peak


class MelodyWalkTask(BaseMathTask):
    TASK_TYPE = "melody_walk"
    TASK_TYPES = ["final", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.start = random.randint(48, 72)
        self.intervals = [random.choice(INTERVALS) for _ in range(self.n)]
        self.pitches, self.peak = walk_melody(self.start, self.intervals)
        self.final_pitch = self.pitches[-1]
        self.answer = self.final_pitch if self.task_type == "final" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{interval:+d}" for interval in self.intervals)
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, interval=f"{interval:+d}", pitch=pitch)
            for index, (interval, pitch) in enumerate(zip(self.intervals, self.pitches), 1)
        ]
        steps.append(texts.t("s3", self.language, final=self.final_pitch, peak=self.peak))
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
