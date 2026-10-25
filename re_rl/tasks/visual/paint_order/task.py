"""PaintOrderTask — клетки после перекрытия прямоугольников.

Более поздний прямоугольник закрывает более ранний. Номер в легенде — порядок покраски.
Число прямоугольников растёт с уровнем. Их положение есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, get_font

Rect = Tuple[int, int, int, int]
COLORS = [
    (38, 139, 210), (220, 50, 47), (46, 160, 67), (230, 170, 20),
    (140, 70, 190), (240, 120, 30), (0, 150, 160), (180, 40, 90),
    (70, 90, 200), (120, 80, 40),
]


def paint_trace(rows: int, cols: int, rects: Sequence[Rect]) -> List[Tuple[int, int]]:
    grid = [[-1] * cols for _ in range(rows)]
    trace = []
    for index, (row, col, height, width) in enumerate(rects):
        for rr in range(row, row + height):
            for cc in range(col, col + width):
                grid[rr][cc] = index
        cover = sum(cell >= 0 for line in grid for cell in line)
        first = sum(cell == 0 for line in grid for cell in line)
        trace.append((cover, first))
    return trace


class PaintOrderTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "paint_order"
    TASK_TYPES = ["cover", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }
    CELL = 18

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.side = self.n + 2
        self.rects: List[Rect] = []
        for _ in range(self.n):
            height = random.randint(2, max(2, self.side // 2))
            width = random.randint(2, max(2, self.side // 2))
            row = random.randint(0, self.side - height)
            col = random.randint(0, self.side - width)
            self.rects.append((row, col, height, width))
        self.trace = paint_trace(self.side, self.side, self.rects)
        self.cover = self.trace[-1][0]
        self.first = self.trace[-1][1]
        self.answer = self.cover if self.task_type == "cover" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "cover" else "s1"
        return texts.t(key, language)

    def render_image(self):
        cell = self.CELL
        board = self.side * cell
        legend = 64
        image = Image.new("RGB", (board + legend, max(board, self.n * 22) + 4), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for index, (row, col, height, width) in enumerate(self.rects):
            x0 = col * cell
            y0 = row * cell
            draw.rectangle(
                [x0, y0, x0 + width * cell - 1, y0 + height * cell - 1],
                fill=COLORS[index],
            )
        for index in range(self.side + 1):
            pos = index * cell
            draw.line([(0, pos), (board, pos)], fill=(230, 230, 226))
            draw.line([(pos, 0), (pos, board)], fill=(230, 230, 226))
        font = get_font(14)
        for index in range(self.n):
            y = 4 + index * 22
            draw.rectangle([board + 8, y, board + 26, y + 16], fill=COLORS[index], outline=(20, 20, 20))
            draw.text((board + 30, y), str(index + 1), fill=(20, 20, 20), font=font)
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cover=cover, first=first)
            for index, (cover, first) in enumerate(self.trace, 1)
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
