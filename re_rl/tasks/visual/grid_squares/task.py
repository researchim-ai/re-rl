"""GridSquaresTask — все квадраты на клетчатом прямоугольнике.

Размеры сетки есть только на картинке. Квадрат может занимать одну клетку или больше.
Число возможных размеров стороны растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin


def square_counts(rows: int, cols: int) -> List[int]:
    side = min(rows, cols)
    return [(rows - k + 1) * (cols - k + 1) for k in range(1, side + 1)]


class GridSquaresTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "grid_squares"
    TASK_TYPES = ["all", "size_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }
    CELL = 36

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rows = self.n
        self.cols = self.n + random.randint(0, 2)
        self.counts = square_counts(self.rows, self.cols)
        self.k = random.randint(1, self.n)
        self.total = sum(self.counts)
        self.at_k = self.counts[self.k - 1]
        self.answer = self.total if self.task_type == "all" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "all" else "s1"
        return texts.t(key, language, k=self.k)

    def render_image(self):
        cell = self.CELL
        width = self.cols * cell + 4
        height = self.rows * cell + 4
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for row in range(self.rows + 1):
            y = 2 + row * cell
            draw.line([(2, y), (2 + self.cols * cell, y)], fill=(25, 25, 25), width=3)
        for col in range(self.cols + 1):
            x = 2 + col * cell
            draw.line([(x, 2), (x, 2 + self.rows * cell)], fill=(25, 25, 25), width=3)
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, count=count)
            for index, count in enumerate(self.counts, 1)
        ]
        steps.append(texts.t("s3", self.language, total=self.total, k=self.k, at_k=self.at_k))
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
