"""ArrowPathTask — ломаная на клетчатой сетке.

Кружок — начало, квадрат — конец. Отрезок соединяет соседние узлы.
Число отрезков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

Point = Tuple[int, int]
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def count_turns(points: Sequence[Point]) -> int:
    turns = 0
    for index in range(1, len(points) - 1):
        before = (points[index][0] - points[index - 1][0], points[index][1] - points[index - 1][1])
        after = (points[index + 1][0] - points[index][0], points[index + 1][1] - points[index][1])
        if before != after:
            turns += 1
    return turns


def make_path(segments: int) -> List[Point]:
    for _ in range(60):
        x = y = 0
        seen = {(0, 0)}
        points = [(0, 0)]
        previous = None
        stuck = False
        for _step in range(segments):
            options = []
            for dx, dy in DIRS:
                nxt = (x + dx, y + dy)
                if nxt not in seen:
                    options.append((dx, dy))
            if not options:
                stuck = True
                break
            if previous in options and random.random() < 0.45:
                dx, dy = previous
            else:
                dx, dy = random.choice(options)
            previous = (dx, dy)
            x, y = x + dx, y + dy
            seen.add((x, y))
            points.append((x, y))
        if not stuck and len(points) == segments + 1:
            min_x = min(point[0] for point in points)
            min_y = min(point[1] for point in points)
            return [(point[0] - min_x, point[1] - min_y) for point in points]
    return [(index, 0) for index in range(segments + 1)]


class ArrowPathTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "arrow_path"
    TASK_TYPES = ["steps", "turns"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }
    CELL = 40

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.points = make_path(self.n)
        self.turns = count_turns(self.points)
        self.answer = self.n if self.task_type == "steps" else self.turns
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "steps" else "s1"
        return texts.t(key, language)

    def render_image(self):
        cell = self.CELL
        max_x = max(point[0] for point in self.points)
        max_y = max(point[1] for point in self.points)
        pad = 28
        width = max_x * cell + 2 * pad
        height = max_y * cell + 2 * pad
        image = Image.new("RGB", (max(width, 80), max(height, 80)), (248, 248, 246))
        draw = ImageDraw.Draw(image)

        def pixel(point):
            return pad + point[0] * cell, pad + (max_y - point[1]) * cell

        for x in range(max_x + 1):
            for y in range(max_y + 1):
                cx, cy = pixel((x, y))
                draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(180, 180, 176))
        for start, end in zip(self.points, self.points[1:]):
            draw.line([pixel(start), pixel(end)], fill=(24, 78, 119), width=6)
        sx, sy = pixel(self.points[0])
        ex, ey = pixel(self.points[-1])
        draw.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=(32, 128, 64), outline=(10, 10, 10), width=2)
        draw.rectangle([ex - 10, ey - 10, ex + 10, ey + 10], fill=(176, 48, 32), outline=(10, 10, 10), width=2)
        return image

    def solve(self):
        steps = []
        for index, (start, end) in enumerate(zip(self.points, self.points[1:]), 1):
            steps.append(texts.t(
                "s2", self.language, i=index,
                x0=start[0], y0=start[1], x1=end[0], y1=end[1],
            ))
        steps.append(texts.t("s3", self.language, steps=self.n, turns=self.turns))
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
