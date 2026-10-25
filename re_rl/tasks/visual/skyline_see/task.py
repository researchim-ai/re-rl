"""SkylineSeeTask — здания, видимые слева.

Здание видно, если оно строго выше каждого здания левее себя. Равная высота его закрывает.
Число зданий растёт с уровнем. Высоты есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin


def skyline_trace(heights: Sequence[int]) -> List[Tuple[int, int, int]]:
    best = 0
    visible = 0
    last = 0
    trace = []
    for index, height in enumerate(heights, 1):
        if height > best:
            best = height
            visible += 1
            last = index
        trace.append((visible, last, best))
    return trace


class SkylineSeeTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "skyline_see"
    TASK_TYPES = ["visible", "last"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }
    CELL_W = 28
    CELL_H = 16

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.heights = [random.randint(1, 6) for _ in range(self.n)]
        self.trace = skyline_trace(self.heights)
        self.visible = self.trace[-1][0]
        self.last = self.trace[-1][1]
        self.answer = self.visible if self.task_type == "visible" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "visible" else "s1"
        return texts.t(key, language)

    def render_image(self):
        margin = 36
        base = 12 + 6 * self.CELL_H
        width = margin + self.n * self.CELL_W + 8
        height = base + 16
        image = Image.new("RGB", (width, height), (248, 248, 246))
        draw = ImageDraw.Draw(image)
        draw.line([(margin - 4, base), (width - 6, base)], fill=(40, 40, 40), width=3)
        for index, height_units in enumerate(self.heights):
            x0 = margin + index * self.CELL_W
            y0 = base - height_units * self.CELL_H
            draw.rectangle([x0, y0, x0 + self.CELL_W - 1, base], fill=(32, 74, 128), outline=(15, 15, 15))
        draw.ellipse([8, base // 2 - 8, 24, base // 2 + 8], fill=(240, 240, 240), outline=(20, 20, 20), width=2)
        draw.polygon([(26, base // 2), (34, base // 2 - 6), (34, base // 2 + 6)], fill=(32, 140, 70))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, height=height, visible=visible, last=last, best=best)
            for index, (height, (visible, last, best)) in enumerate(zip(self.heights, self.trace), 1)
        ]
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
