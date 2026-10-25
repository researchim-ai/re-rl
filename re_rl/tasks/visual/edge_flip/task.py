"""EdgeFlipTask — границы между клетками разного цвета.

Считаются общие стороны, по которым цвета различаются. Горизонтальные и вертикальные границы ведутся отдельно.
Сторона сетки растёт с уровнем. Цвета есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

Grid = Sequence[Sequence[int]]
PALETTE = [(236, 232, 214), (32, 74, 128), (196, 64, 48)]


def edge_trace(grid: Grid) -> List[Tuple[int, int, int, int]]:
    size = len(grid)
    flat = 0
    rise = 0
    trace = []
    for row in range(size):
        row_flat = 0
        row_rise = 0
        for col in range(size - 1):
            if grid[row][col] != grid[row][col + 1]:
                row_flat += 1
        if row:
            for col in range(size):
                if grid[row - 1][col] != grid[row][col]:
                    row_rise += 1
        flat += row_flat
        rise += row_rise
        trace.append((row_flat, flat, row_rise, rise))
    return trace


class EdgeFlipTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "edge_flip"
    TASK_TYPES = ["flat", "rise"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }
    CELL = 34

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.grid = [
            [random.randint(0, 2) for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.trace = edge_trace(self.grid)
        self.flat = self.trace[-1][1]
        self.rise = self.trace[-1][3]
        self.answer = self.flat if self.task_type == "flat" else self.rise
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "flat" else "s1"
        return texts.t(key, language)

    def render_image(self):
        cell = self.CELL
        side = self.n * cell + 3
        image = Image.new("RGB", (side, side), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for row in range(self.n):
            for col in range(self.n):
                x0 = 1 + col * cell
                y0 = 1 + row * cell
                draw.rectangle(
                    [x0, y0, x0 + cell - 2, y0 + cell - 2],
                    fill=PALETTE[self.grid[row][col]],
                    outline=(30, 30, 30),
                )
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, row_flat=row_flat, flat=flat, row_rise=row_rise, rise=rise)
            for index, (row_flat, flat, row_rise, rise) in enumerate(self.trace, 1)
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
