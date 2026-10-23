"""ClockRowTask — несколько циферблатов в ряд.

Часовая стрелка короче минутной. Сверху отмечено 12.
Число часов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin


def hand_tip(cx: float, cy: float, length: float, degrees_from_twelve: float) -> Tuple[float, float]:
    radians = math.radians(degrees_from_twelve)
    return cx + math.sin(radians) * length, cy - math.cos(radians) * length


def hour_degrees(hour: int, minute: int) -> float:
    return (hour % 12) * 30 + minute * 0.5


def minute_degrees(minute: int) -> float:
    return minute * 6


class ClockRowTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "clock_row"
    TASK_TYPES = ["hour_sum", "minute_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }
    RADIUS = 58

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.clocks = [
            (random.randint(1, 12), random.randrange(0, 60, 5)) for _ in range(self.n)
        ]
        self.hour_sum = sum(hour for hour, _minute in self.clocks)
        self.minute_sum = sum(minute for _hour, minute in self.clocks)
        self.answer = self.hour_sum if self.task_type == "hour_sum" else self.minute_sum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "hour_sum" else "s1"
        return texts.t(key, language)

    def render_image(self):
        radius = self.RADIUS
        slot = radius * 2 + 28
        width = self.n * slot + 16
        height = radius * 2 + 52
        image = Image.new("RGB", (width, height), (246, 246, 244))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.load_default(size=18)
        except TypeError:
            font = ImageFont.load_default()
        for index, (hour, minute) in enumerate(self.clocks):
            cx = 16 + index * slot + radius + 8
            cy = 16 + radius
            self._draw_clock(draw, font, cx, cy, radius, hour, minute)
            draw.text((cx - 4, cy + radius + 8), str(index + 1), fill=(30, 30, 30), font=font)
        return image

    def _draw_clock(self, draw, font, cx, cy, radius, hour, minute):
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(255, 255, 255), outline=(20, 20, 20), width=3,
        )
        for mark in range(12):
            outer = hand_tip(cx, cy, radius - 4, mark * 30)
            inner = hand_tip(cx, cy, radius - (14 if mark % 3 == 0 else 8), mark * 30)
            draw.line([inner, outer], fill=(20, 20, 20), width=3 if mark % 3 == 0 else 1)
        labels = (("12", 0, -radius + 18), ("3", radius - 22, -8), ("6", -6, radius - 28), ("9", -radius + 10, -8))
        for label, dx, dy in labels:
            draw.text((cx + dx, cy + dy), label, fill=(20, 20, 20), font=font)
        hour_end = hand_tip(cx, cy, radius * 0.48, hour_degrees(hour, minute))
        minute_end = hand_tip(cx, cy, radius * 0.72, minute_degrees(minute))
        draw.line([(cx, cy), hour_end], fill=(20, 20, 20), width=5)
        draw.line([(cx, cy), minute_end], fill=(20, 90, 160), width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(20, 20, 20))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, hour=hour, minute=minute)
            for index, (hour, minute) in enumerate(self.clocks, 1)
        ]
        steps.append(texts.t(
            "s3", self.language, hour_sum=self.hour_sum, minute_sum=self.minute_sum,
        ))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
