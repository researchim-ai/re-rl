"""ArrowTurnTask — левые повороты в ряду стрелок.

Поворот налево — смена направления на четверть оборота против часовой стрелки.
Первая стрелка поворота не даёт. Число стрелок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

VECTORS = ((0, -1), (1, 0), (0, 1), (-1, 0))


def arrow_trace(directions: Sequence[int]) -> List[Tuple[int, int, int]]:
    lefts = 0
    trace = []
    for index, direction in enumerate(directions):
        turned = 0
        if index and (directions[index - 1] - direction) % 4 == 1:
            turned = 1
            lefts += 1
        trace.append((direction + 1, turned, lefts))
    return trace


class ArrowTurnTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "arrow_turn"
    TASK_TYPES = ["lefts", "last"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }
    BOX = 52

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.directions = [random.randint(0, 3) for _ in range(self.n)]
        self.trace = arrow_trace(self.directions)
        self.lefts = self.trace[-1][2]
        self.last = self.trace[-1][0]
        self.answer = self.lefts if self.task_type == "lefts" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "lefts" else "s1"
        return texts.t(key, language)

    def render_image(self):
        box = self.BOX
        gap = 10
        width = 8 + self.n * box + (self.n - 1) * gap
        height = box + 16
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for index, direction in enumerate(self.directions):
            x = 8 + index * (box + gap)
            y = 8
            draw.rectangle([x, y, x + box, y + box], outline=(80, 80, 80), width=2)
            self._arrow(draw, x, y, box, direction)
        return image

    @staticmethod
    def _arrow(draw, x: int, y: int, box: int, direction: int) -> None:
        cx = x + box // 2
        cy = y + box // 2
        dx, dy = VECTORS[direction]
        tail = (cx - dx * 14, cy - dy * 14)
        tip = (cx + dx * 16, cy + dy * 16)
        draw.line([tail, tip], fill=(32, 74, 128), width=5)
        px, py = -dy, dx
        head = [
            tip,
            (tip[0] - dx * 12 + px * 7, tip[1] - dy * 12 + py * 7),
            (tip[0] - dx * 12 - px * 7, tip[1] - dy * 12 - py * 7),
        ]
        draw.polygon(head, fill=(32, 74, 128))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, turned=turned, lefts=lefts)
            for index, (code, turned, lefts) in enumerate(self.trace, 1)
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
