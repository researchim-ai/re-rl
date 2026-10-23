"""BlockTowerTask — столбцы блоков на картинке.

Высоты видны только на рисунке. Столбцы нумеруются слева направо.
Число столбцов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin


class BlockTowerTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "block_tower"
    TASK_TYPES = ["total", "height"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "h": 3}, 2: {"n": 2, "h": 4}, 3: {"n": 3, "h": 4},
        4: {"n": 3, "h": 5}, 5: {"n": 4, "h": 5}, 6: {"n": 5, "h": 5},
        7: {"n": 6, "h": 6}, 8: {"n": 7, "h": 6}, 9: {"n": 8, "h": 6},
        10: {"n": 10, "h": 6},
    }
    CELL = 34
    GAP = 12

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["h"]))
        self.heights = [random.randint(1, limit) for _ in range(self.n)]
        self.k = random.randint(1, self.n)
        self.total = sum(self.heights)
        self.column = self.heights[self.k - 1]
        self.answer = self.total if self.task_type == "total" else self.column
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, k=self.k)

    def render_image(self):
        cell, gap = self.CELL, self.GAP
        top = max(self.heights) * cell + 16
        width = self.n * cell + (self.n + 1) * gap
        height = top + 36
        image = Image.new("RGB", (width, height), (248, 244, 236))
        draw = ImageDraw.Draw(image)
        ground = top + 2
        draw.line([(8, ground), (width - 8, ground)], fill=(60, 50, 40), width=3)
        for index, blocks in enumerate(self.heights):
            x0 = gap + index * (cell + gap)
            for level in range(blocks):
                y1 = ground - (level + 1) * cell
                y0 = y1 + 3
                draw.rounded_rectangle(
                    [x0, y0, x0 + cell - 2, y1 + cell - 2],
                    radius=4, fill=(196, 122, 74), outline=(40, 30, 20), width=2,
                )
            label = str(index + 1)
            draw.text((x0 + cell // 2 - 4, ground + 8), label, fill=(30, 30, 30))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, height=height)
            for index, height in enumerate(self.heights, 1)
        ]
        steps.append(texts.t("s3", self.language, total=self.total, k=self.k, column=self.column))
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
