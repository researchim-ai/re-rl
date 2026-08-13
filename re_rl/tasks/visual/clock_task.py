"""Чтение аналоговых часов (визуальная задача, PIL).

Нужно определить время по циферблату. Ответ — в формате ``Ч:ММ``.
Сложность управляет точностью минут (кратность 15 → 5 → 1).
"""

import math
import random
import re
from typing import Any, ClassVar, Dict

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, get_font
from re_rl.tasks.math.logic import _logic_utils as U


class ClockReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "clock_read"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"step": 15}, 2: {"step": 15}, 3: {"step": 15}, 4: {"step": 5}, 5: {"step": 5},
        6: {"step": 5}, 7: {"step": 5}, 8: {"step": 1}, 9: {"step": 1}, 10: {"step": 1},
    }
    SIZE = 260

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.step = int(p["step"])
        self.hour = random.randint(1, 12)
        self.minute = random.randrange(0, 60, self.step)
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _hand(self, draw, cx, cy, angle_deg, length, width, fill):
        th = math.radians(angle_deg)
        x = cx + length * math.sin(th)
        y = cy - length * math.cos(th)
        draw.line([(cx, cy), (x, y)], fill=fill, width=width)

    def render_image(self):
        S = self.SIZE
        img = Image.new("RGB", (S, S), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        cx = cy = S / 2
        r = S / 2 - 12
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 0), width=3)
        font = get_font(18)
        for h in range(1, 13):
            th = math.radians(h * 30)
            # деление
            x1 = cx + (r - 8) * math.sin(th); y1 = cy - (r - 8) * math.cos(th)
            x2 = cx + r * math.sin(th); y2 = cy - r * math.cos(th)
            draw.line([(x1, y1), (x2, y2)], fill=(0, 0, 0), width=2)
            # цифра
            nx = cx + (r - 26) * math.sin(th); ny = cy - (r - 26) * math.cos(th)
            s = str(h)
            bb = draw.textbbox((0, 0), s, font=font)
            draw.text((nx - (bb[2] - bb[0]) / 2, ny - (bb[3] - bb[1]) / 2 - bb[1]), s,
                      fill=(0, 0, 0), font=font)
        minute_angle = self.minute * 6
        hour_angle = (self.hour % 12) * 30 + self.minute * 0.5
        self._hand(draw, cx, cy, hour_angle, r * 0.5, 6, (0, 0, 0))
        self._hand(draw, cx, cy, minute_angle, r * 0.8, 4, (38, 139, 210))
        draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(0, 0, 0))
        return img

    def _time_str(self) -> str:
        return f"{self.hour}:{self.minute:02d}"

    def _descr(self, language):
        ru = language == "ru"
        return ("Определите время на циферблате. Ответ дайте в формате Ч:ММ (например, 3:45)."
                if ru else
                "Read the time on the clock. Answer in H:MM format (e.g., 3:45).")

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Короткая стрелка указывает часы, длинная — минуты." if ru else
             "The short hand shows hours, the long hand shows minutes."),
            (f"Время: {self._time_str()}." if ru else f"Time: {self._time_str()}.")]
        self.final_answer = self._time_str()

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        txt = U.clean(prediction)
        for hh, mm in re.findall(r"(\d{1,2})\s*[:.\-]\s*(\d{1,2})", txt):
            if int(mm) == self.minute and int(hh) % 12 == self.hour % 12:
                return 1.0
        return 0.0

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
