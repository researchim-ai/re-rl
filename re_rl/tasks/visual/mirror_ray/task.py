"""MirrorRayTask — луч среди двух видов зеркал.

Черта из левого верхнего угла в правый нижний и черта из левого нижнего в правый верхний поворачивают луч по-разному.
Луч входит слева и идёт направо. Сторона сетки растёт с уровнем.
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


def turn(dr: int, dc: int, kind: int) -> Tuple[int, int]:
    if kind == 1:
        return dc, dr
    return -dc, -dr


def ray_trace(grid: Grid, start: int) -> Tuple[List[Tuple[int, int, int]], int, int]:
    rows = len(grid)
    cols = len(grid[0])
    row, col = start, 0
    dr, dc = 0, 1
    hits = 0
    seen = set()
    trace = []
    side = 0
    for _ in range(rows * cols + 2):
        state = (row, col, dr, dc)
        if state in seen:
            return trace, hits, 0
        seen.add(state)
        if grid[row][col]:
            hits += 1
            dr, dc = turn(dr, dc, grid[row][col])
        trace.append((row + 1, col + 1, hits))
        nr, nc = row + dr, col + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            if nc < 0:
                side = 1
            elif nc >= cols:
                side = 2
            elif nr < 0:
                side = 3
            else:
                side = 4
            return trace, hits, side
        row, col = nr, nc
    return trace, hits, 0


def make_mirrors(size: int) -> Tuple[List[List[int]], int, List[Tuple[int, int, int]], int, int]:
    for _ in range(50):
        grid = [[0] * size for _ in range(size)]
        cells = [(row, col) for row in range(size) for col in range(size)]
        random.shuffle(cells)
        for row, col in cells[: max(1, size // 2)]:
            grid[row][col] = random.choice((1, 2))
        start = random.randrange(size)
        trace, hits, side = ray_trace(grid, start)
        if side:
            return grid, start, trace, hits, side
    grid = [[0] * size for _ in range(size)]
    trace, hits, side = ray_trace(grid, 0)
    return grid, 0, trace, hits, side


class MirrorRayTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "mirror_ray"
    TASK_TYPES = ["hits", "side"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }
    CELL = 36

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.grid, self.start, self.trace, self.hits, self.side = make_mirrors(self.n)
        assert self.side
        self.answer = self.hits if self.task_type == "hits" else self.side
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "hits" else "s1"
        return texts.t(key, language)

    def render_image(self):
        cell = self.CELL
        margin = 28
        side = self.n * cell
        image = Image.new("RGB", (side + margin + 4, side + 4), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        origin = margin
        for row in range(self.n):
            for col in range(self.n):
                x0 = origin + col * cell
                y0 = 2 + row * cell
                draw.rectangle([x0, y0, x0 + cell, y0 + cell], outline=(180, 180, 176))
                kind = self.grid[row][col]
                if kind == 1:
                    draw.line([(x0 + 6, y0 + 6), (x0 + cell - 6, y0 + cell - 6)], fill=(20, 20, 20), width=4)
                elif kind == 2:
                    draw.line([(x0 + 6, y0 + cell - 6), (x0 + cell - 6, y0 + 6)], fill=(20, 20, 20), width=4)
        cy = 2 + self.start * cell + cell // 2
        draw.polygon([(6, cy), (margin - 6, cy - 8), (margin - 6, cy + 8)], fill=(32, 140, 70))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, row=row, col=col, hits=hits)
            for row, col, hits in self.trace
        ]
        steps.append(texts.t("s3", self.language, hits=self.hits, side=self.side))
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
