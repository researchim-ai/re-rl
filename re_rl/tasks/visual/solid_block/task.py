"""SolidBlockTask — сплошные тёмные квадраты.

Квадрат сплошной, если все его клетки тёмные. Сторона и число квадратов 2 на 2 считаются по сетке.
Сторона сетки растёт с уровнем. Клетки есть только на картинке.
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


def solid_trace(grid: Grid) -> Tuple[List[Tuple[int, int]], int]:
    size = len(grid)
    twos = 0
    trace = []
    for row in range(size):
        added = 0
        if row:
            for col in range(size - 1):
                block = (
                    grid[row - 1][col] and grid[row - 1][col + 1]
                    and grid[row][col] and grid[row][col + 1]
                )
                if block:
                    added += 1
        twos += added
        trace.append((added, twos))
    best = 0
    for side in range(size, 0, -1):
        found = False
        for row in range(size - side + 1):
            for col in range(size - side + 1):
                if all(grid[row + dr][col + dc] for dr in range(side) for dc in range(side)):
                    found = True
                    break
            if found:
                break
        if found:
            best = side
            break
    return trace, best


class SolidBlockTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "solid_block"
    TASK_TYPES = ["side", "twos"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }
    CELL = 32

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.grid = [
            [1 if random.random() < 0.55 else 0 for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.trace, self.side = solid_trace(self.grid)
        self.twos = self.trace[-1][1]
        self.answer = self.side if self.task_type == "side" else self.twos
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "side" else "s1"
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
                fill = (20, 20, 20) if self.grid[row][col] else (250, 250, 248)
                draw.rectangle([x0, y0, x0 + cell - 2, y0 + cell - 2], fill=fill, outline=(170, 170, 166))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, added=added, twos=twos)
            for index, (added, twos) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, side=self.side, twos=self.twos))
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
