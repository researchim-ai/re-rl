"""MeetingMotionTask — момент и место встречи двух тел на прямой.

Встречный случай: скорости направлены друг к другу.
Догон: оба едут вправо, заднее быстрее. Время и координата встречи целые.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class MeetingMotionTask(BaseMathTask):
    TASK_TYPE = "meeting_motion"
    TASK_TYPES = ["time", "position"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 3, "t": 4}, 2: {"v": 4, "t": 5}, 3: {"v": 4, "t": 6},
        4: {"v": 5, "t": 6}, 5: {"v": 5, "t": 8}, 6: {"v": 6, "t": 8},
        7: {"v": 6, "t": 10}, 8: {"v": 8, "t": 10}, 9: {"v": 8, "t": 12},
        10: {"v": 10, "t": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.mode = random.choice(["head_on", "chase"])
        self.time = random.randint(1, int(p["t"]))
        if self.mode == "head_on":
            self.va = random.randint(1, int(p["v"]))
            self.vb = random.randint(1, int(p["v"]))
            self.xa = random.randint(0, 12)
            self.xb = self.xa + self.time * (self.va + self.vb)
            self.place = self.xa + self.va * self.time
        else:
            self.va = random.randint(1, max(1, int(p["v"]) - 1))
            self.vb = self.va + random.randint(1, int(p["v"]))
            self.xb = random.randint(0, 12)
            self.xa = self.xb + self.time * (self.vb - self.va)
            self.place = self.xa + self.va * self.time
        self.answer = self.time if self.task_type == "time" else self.place
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.mode == "head_on":
            story = ((texts.t('s1', language, xa=self.xa, va=self.va, xb=self.xb, vb=self.vb)))
        else:
            story = ((texts.t('s2', language, xa=self.xa, va=self.va, xb=self.xb, vb=self.vb)))
        if self.task_type == "time":
            ask = ((texts.t('s3', language)))
        else:
            ask = ((texts.t('s4', language)))
        return f"{story} {ask}"

    def solve(self):
        step = ((texts.t('s0', self.language, time=self.time, place=self.place)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
