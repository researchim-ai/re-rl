"""MirrorFaultTask — пары клеток, которые ломают зеркальную симметрию.

Ось вертикальная. Сравниваются клетки, одинаково удалённые от левого и правого края.
Число строк растёт с уровнем. Сама сетка есть только на картинке.
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


def mirror_trace(grid: Grid) -> List[Tuple[int, int, int]]:
    width = len(grid[0])
    flips = 0
    bad_rows = 0
    trace = []
    for row in grid:
        bad = 0
        for col in range(width // 2):
            if row[col] != row[width - 1 - col]:
                bad += 1
        flips += bad
        if bad:
            bad_rows += 1
        trace.append((bad, flips, bad_rows))
    return trace


class MirrorFaultTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "mirror_fault"
    TASK_TYPES = ["pairs", "rows"]

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
            [random.randint(0, 1) for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.trace = mirror_trace(self.grid)
        self.pairs = self.trace[-1][1]
        self.rows = self.trace[-1][2]
        self.answer = self.pairs if self.task_type == "pairs" else self.rows
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "pairs" else "s1"
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
                fill = (32, 74, 128) if self.grid[row][col] else (244, 244, 240)
                draw.rectangle([x0, y0, x0 + cell - 2, y0 + cell - 2], fill=fill, outline=(20, 20, 20))
        return image

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bad=bad, pairs=pairs, rows=rows)
            for index, (bad, pairs, rows) in enumerate(self.trace, 1)
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
