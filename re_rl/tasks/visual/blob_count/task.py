"""BlobCountTask — число фигур из тёмных клеток.

Клетки одной фигуры делят сторону. Касание углом фигуры не соединяет.
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


def blob_trace(grid: Grid) -> List[Tuple[int, int]]:
    rows = len(grid)
    cols = len(grid[0])
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
    size: Dict[Tuple[int, int], int] = {}

    def find(node: Tuple[int, int]) -> Tuple[int, int]:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    parts = 0
    largest = 0
    trace = []
    for row in range(rows):
        for col in range(cols):
            if not grid[row][col]:
                continue
            node = (row, col)
            parent[node] = node
            size[node] = 1
            parts += 1
            root = node
            for dr, dc in ((-1, 0), (0, -1)):
                nr, nc = row + dr, col + dc
                if nr < 0 or nc < 0 or not grid[nr][nc]:
                    continue
                other = find((nr, nc))
                root = find(node)
                if other != root:
                    parent[other] = root
                    size[root] += size[other]
                    parts -= 1
            largest = max(largest, size[find(node)])
        trace.append((parts, largest))
    return trace


class BlobCountTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "blob_count"
    TASK_TYPES = ["parts", "largest"]

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
            [1 if random.random() < 0.45 else 0 for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.grid[self.n // 2][self.n // 2] = 1
        self.trace = blob_trace(self.grid)
        self.parts = self.trace[-1][0]
        self.largest = self.trace[-1][1]
        self.answer = self.parts if self.task_type == "parts" else self.largest
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "parts" else "s1"
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
                draw.rectangle([x0, y0, x0 + cell - 2, y0 + cell - 2], fill=fill, outline=(190, 190, 186))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, parts=parts, largest=largest)
            for index, (parts, largest) in enumerate(self.trace, 1)
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
