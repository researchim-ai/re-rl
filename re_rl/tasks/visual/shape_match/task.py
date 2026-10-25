"""ShapeMatchTask — совпадение фигуры после поворота.

Поворот на прямой угол разрешён. Отражение совпадением не считается.
Число фигур справа растёт с уровнем. Клетки фигур есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

Cell = Tuple[int, int]
Shape = Sequence[Cell]

SHAPES: List[List[Cell]] = [
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 1), (0, 2), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],
]


def normalize(cells: Shape):
    min_row = min(row for row, _col in cells)
    min_col = min(col for _row, col in cells)
    return frozenset((row - min_row, col - min_col) for row, col in cells)


def rotations(cells: Shape) -> List[frozenset]:
    current = list(cells)
    found = []
    for _ in range(4):
        found.append(normalize(current))
        current = [(col, -row) for row, col in current]
    return found


def same_turn(left: Shape, right: Shape) -> bool:
    return normalize(right) in rotations(left)


class ShapeMatchTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "shape_match"
    TASK_TYPES = ["matches", "here"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 7}, 10: {"n": 8},
    }
    CELL = 22
    BOX = 4

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        base = random.choice(SHAPES)
        self.target = sorted(random.choice(rotations(base)))
        self.candidates: List[List[Cell]] = []
        for _ in range(self.n):
            if random.random() < 0.55:
                shown = random.choice(rotations(self.target))
            else:
                shown = random.choice(rotations(random.choice(SHAPES)))
            self.candidates.append(sorted(shown))
        self.flags = [1 if same_turn(self.target, cand) else 0 for cand in self.candidates]
        self.matches = sum(self.flags)
        self.k = random.randint(1, self.n)
        self.here = self.flags[self.k - 1]
        self.answer = self.matches if self.task_type == "matches" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "matches" else "s1"
        return texts.t(key, language, k=self.k)

    def render_image(self):
        cell = self.CELL
        box = self.BOX * cell
        gap = 16
        figures = 1 + self.n
        width = 8 + figures * box + (figures - 1) * gap
        height = box + 16
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        figures_cells = [self.target] + self.candidates
        for index, cells in enumerate(figures_cells):
            x = 8 + index * (box + gap)
            y = 8
            outline = (32, 140, 70) if index == 0 else (80, 80, 80)
            width_px = 4 if index == 0 else 2
            draw.rectangle([x, y, x + box, y + box], outline=outline, width=width_px)
            for row, col in cells:
                x0 = x + col * cell
                y0 = y + row * cell
                draw.rectangle(
                    [x0 + 2, y0 + 2, x0 + cell - 2, y0 + cell - 2],
                    fill=(32, 74, 128),
                )
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, flag=flag, matches=sum(self.flags[:index]))
            for index, flag in enumerate(self.flags, 1)
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
