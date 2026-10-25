"""InkSpreadTask — растекание краски от отмеченной клетки.

Серые клетки — стены. Краска идёт по белым в четыре стороны и через стены не проходит.
Число строк растёт с уровнем. Сетка есть только на картинке.
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


def ink_trace(grid: Grid, source: Tuple[int, int]) -> List[Tuple[int, int, int]]:
    rows = len(grid)
    cols = len(grid[0])
    seen = [[0] * cols for _ in range(rows)]
    start_row, start_col = source
    stack = [(start_row, start_col)]
    seen[start_row][start_col] = 1
    while stack:
        row, col = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and not grid[nr][nc] and not seen[nr][nc]:
                seen[nr][nc] = 1
                stack.append((nr, nc))
    reached = 0
    missed = 0
    trace = []
    for row in range(rows):
        for col in range(cols):
            if grid[row][col]:
                continue
            if seen[row][col]:
                reached += 1
            else:
                missed += 1
        trace.append((reached, missed))
    return trace


class InkSpreadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "ink_spread"
    TASK_TYPES = ["reached", "missed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }
    CELL = 32

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.grid = [
            [1 if random.random() < 0.34 else 0 for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.source = (random.randrange(self.n), random.randrange(self.n))
        self.grid[self.source[0]][self.source[1]] = 0
        self.trace = ink_trace(self.grid, self.source)
        self.reached = self.trace[-1][0]
        self.missed = self.trace[-1][1]
        self.answer = self.reached if self.task_type == "reached" else self.missed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "reached" else "s1"
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
                fill = (90, 90, 92) if self.grid[row][col] else (248, 248, 246)
                draw.rectangle([x0, y0, x0 + cell - 2, y0 + cell - 2], fill=fill, outline=(30, 30, 30))
        sr, sc = self.source
        cx = 1 + sc * cell + cell // 2 - 1
        cy = 1 + sr * cell + cell // 2 - 1
        radius = cell // 5
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(200, 40, 40))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, reached=reached, missed=missed)
            for index, (reached, missed) in enumerate(self.trace, 1)
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
