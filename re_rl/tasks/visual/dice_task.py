"""Игральные кости (визуальная задача, PIL).

Подтипы:
- ``sum``         — сумма очков на всех костях;
- ``count_value`` — сколько костей показывают заданное значение.
"""

import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin
from re_rl.tasks.math.logic import _logic_utils as U

# Относительные позиции точек (3×3) для каждого значения 1..6.
_PIPS = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (0, 2), (2, 0), (2, 2)],
    5: [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
    6: [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)],
}


class DiceReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "dice_read"
    TASK_TYPES = ["sum", "count_value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 5}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 8},
    }
    DIE = 80
    GAP = 18

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n = int(p["n"])
        self.faces = [random.randint(1, 6) for _ in range(self.n)]
        if self.task_type == "count_value":
            self.value = random.randint(1, 6)
            self.answer = self.faces.count(self.value)
        else:
            self.answer = sum(self.faces)
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def render_image(self):
        D, G = self.DIE, self.GAP
        w = self.n * D + (self.n + 1) * G
        h = D + 2 * G
        img = Image.new("RGB", (w, h), (245, 245, 245))
        draw = ImageDraw.Draw(img)
        pip_r = D * 0.09
        for i, v in enumerate(self.faces):
            x0 = G + i * (D + G)
            y0 = G
            draw.rounded_rectangle([x0, y0, x0 + D, y0 + D], radius=D * 0.15,
                                   fill=(255, 255, 255), outline=(0, 0, 0), width=3)
            for (r, c) in _PIPS[v]:
                cx = x0 + D * (0.25 + 0.25 * c)
                cy = y0 + D * (0.25 + 0.25 * r)
                draw.ellipse([cx - pip_r, cy - pip_r, cx + pip_r, cy + pip_r], fill=(0, 0, 0))
        return img

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "count_value":
            return (f"На картинке несколько игральных костей. Сколько из них показывают "
                    f"{self.value} очков?" if ru else
                    f"The picture shows several dice. How many of them show {self.value}?")
        return ("На картинке несколько игральных костей. Чему равна сумма всех очков?" if ru else
                "The picture shows several dice. What is the total number of pips?")

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "count_value":
            self.solution_steps = [
                (f"Считаем кости со значением {self.value}." if ru else
                 f"Count dice showing {self.value}."),
                (f"Таких костей: {self.answer}." if ru else f"Count: {self.answer}.")]
        else:
            self.solution_steps = [
                (f"Складываем очки: {' + '.join(map(str, self.faces))}." if ru else
                 f"Add pips: {' + '.join(map(str, self.faces))}."),
                (f"Сумма: {self.answer}." if ru else f"Total: {self.answer}.")]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
