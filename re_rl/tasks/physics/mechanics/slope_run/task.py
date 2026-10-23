"""SlopeRunTask — квадрат скорости на цепочке участков.

На участке квадрат скорости меняется на 2·a·s. Отрицательный результат означает остановку.
Дальше тело не едет. Число участков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Slope = Tuple[int, int]


def run_slopes(segments: Sequence[Slope]) -> List[Tuple[int, int]]:
    speed2 = 0
    stopped = 0
    trace = []
    for index, (accel, length) in enumerate(segments, 1):
        if stopped:
            trace.append((0, stopped))
            continue
        nxt = speed2 + 2 * accel * length
        if nxt < 0:
            speed2 = 0
            stopped = index
        else:
            speed2 = nxt
        trace.append((speed2, stopped))
    return trace


class SlopeRunTask(BaseMathTask):
    TASK_TYPE = "slope_run"
    TASK_TYPES = ["speed2", "stop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 4}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 5}, 8: {"n": 7, "m": 6}, 9: {"n": 8, "m": 6},
        10: {"n": 10, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.segments = []
        for index in range(self.n):
            accel = random.randint(-limit, limit)
            if accel == 0:
                accel = 1 if index % 2 == 0 else -1
            length = random.randint(1, limit)
            self.segments.append((accel, length))
        self.trace = run_slopes(self.segments)
        self.speed2, self.stop = self.trace[-1]
        self.answer = self.speed2 if self.task_type == "speed2" else self.stop
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{accel}, {length}" for accel, length in self.segments)
        key = "s0" if self.task_type == "speed2" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, accel=accel, length=length, speed2=speed2, stop=stop)
            for index, ((accel, length), (speed2, stop)) in enumerate(zip(self.segments, self.trace), 1)
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
