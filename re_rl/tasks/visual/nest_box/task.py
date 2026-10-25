"""NestBoxTask — строгая вложенность прямоугольников.

Прямоугольник лежит внутри другого, только если не касается его границы.
Число прямоугольников растёт с уровнем. Рамки есть только на картинке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

Rect = Tuple[int, int, int, int]
COLORS = [
    (38, 139, 210), (220, 50, 47), (46, 160, 67), (140, 70, 190),
    (240, 120, 30), (0, 150, 160), (180, 40, 90), (70, 90, 200),
]


def contains(outer: Rect, inner: Rect) -> bool:
    top, left, height, width = outer
    row, col, inner_h, inner_w = inner
    return (
        top < row and left < col
        and top + height > row + inner_h
        and left + width > col + inner_w
    )


def nest_trace(rects: Sequence[Rect]) -> List[Tuple[int, int, int]]:
    pairs = 0
    outers = 0
    trace = []
    for index, rect in enumerate(rects):
        held = sum(contains(rect, other) for other_index, other in enumerate(rects) if other_index != index)
        if held:
            outers += 1
        pairs += held
        trace.append((held, pairs, outers))
    return trace


class NestBoxTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "nest_box"
    TASK_TYPES = ["pairs", "outers"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }
    CELL = 16

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.side = self.n + 6
        self.rects = self._build()
        self.trace = nest_trace(self.rects)
        self.pairs = self.trace[-1][1]
        self.outers = self.trace[-1][2]
        self.answer = self.pairs if self.task_type == "pairs" else self.outers
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self) -> List[Rect]:
        rects: List[Rect] = []
        for _ in range(self.n):
            parent = None
            if rects and random.random() < 0.5:
                candidate = random.choice(rects)
                if candidate[2] >= 4 and candidate[3] >= 4:
                    parent = candidate
            if parent is not None:
                top, left, height, width = parent
                inner_h = random.randint(2, height - 2)
                inner_w = random.randint(2, width - 2)
                row = random.randint(top + 1, top + height - inner_h - 1)
                col = random.randint(left + 1, left + width - inner_w - 1)
                rects.append((row, col, inner_h, inner_w))
                continue
            height = random.randint(3, max(3, self.side // 2))
            width = random.randint(3, max(3, self.side // 2))
            row = random.randint(0, self.side - height)
            col = random.randint(0, self.side - width)
            rects.append((row, col, height, width))
        return rects

    def _descr(self, language):
        key = "s0" if self.task_type == "pairs" else "s1"
        return texts.t(key, language)

    def render_image(self):
        cell = self.CELL
        side = self.side * cell + 2
        image = Image.new("RGB", (side, side), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        order = sorted(range(self.n), key=lambda index: self.rects[index][2] * self.rects[index][3], reverse=True)
        for index in order:
            row, col, height, width = self.rects[index]
            color = COLORS[index % len(COLORS)]
            pale = tuple((channel + 255 * 3) // 4 for channel in color)
            x0 = col * cell
            y0 = row * cell
            x1 = x0 + width * cell - 1
            y1 = y0 + height * cell - 1
            draw.rectangle([x0, y0, x1, y1], fill=pale, outline=color, width=3)
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, held=held, pairs=pairs, outers=outers)
            for index, (held, pairs, outers) in enumerate(self.trace, 1)
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
