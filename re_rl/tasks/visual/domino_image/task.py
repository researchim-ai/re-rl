"""DominoImageTask — цепочка костей, поля которой видны только на картинке.

Стык верен, если правое поле совпадает с левым полем следующей кости.
Число костей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.domino_chain.task import first_break
from re_rl.tasks.visual._visual_utils import VisualTaskMixin

PIPS = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (0, 2), (2, 0), (2, 2)],
    5: [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
    6: [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)],
}


def pip_sum(dominoes: List[Tuple[int, int]]) -> int:
    return sum(left + right for left, right in dominoes)


class DominoImageTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "domino_image"
    TASK_TYPES = ["pips", "break"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }
    HALF = 46
    GAP = 16

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        left = random.randint(0, 6)
        self.dominoes: List[Tuple[int, int]] = []
        for _ in range(self.n):
            right = random.randint(0, 6)
            self.dominoes.append((left, right))
            left = right
        if random.randrange(2) == 0:
            junction = random.randrange(self.n - 1)
            required = self.dominoes[junction][1]
            new_left = (required + 1 + random.randrange(6)) % 7
            _old, right = self.dominoes[junction + 1]
            self.dominoes[junction + 1] = (new_left, right)
        self.break_at, self.matched = first_break(self.dominoes)
        self.pips = pip_sum(self.dominoes)
        self.answer = self.pips if self.task_type == "pips" else self.break_at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "pips" else "s1"
        return texts.t(key, language)

    def _draw_half(self, draw, x0, y0, value):
        size = self.HALF
        if value == 0:
            return
        radius = size * 0.08
        for row, col in PIPS[value]:
            cx = x0 + size * (0.25 + 0.25 * col)
            cy = y0 + size * (0.25 + 0.25 * row)
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(20, 20, 20))

    def render_image(self):
        half, gap = self.HALF, self.GAP
        tile = half * 2
        width = self.n * tile + (self.n + 1) * gap
        height = half + 2 * gap + 22
        image = Image.new("RGB", (width, height), (232, 236, 230))
        draw = ImageDraw.Draw(image)
        for index, (left, right) in enumerate(self.dominoes):
            x0 = gap + index * (tile + gap)
            y0 = gap
            draw.rounded_rectangle(
                [x0, y0, x0 + tile, y0 + half],
                radius=8, fill=(255, 255, 255), outline=(20, 20, 20), width=3,
            )
            mid = x0 + half
            draw.line([(mid, y0 + 6), (mid, y0 + half - 6)], fill=(20, 20, 20), width=2)
            self._draw_half(draw, x0, y0, left)
            self._draw_half(draw, mid, y0, right)
            draw.text((x0 + half - 4, y0 + half + 6), str(index + 1), fill=(30, 30, 30))
        return image

    def solve(self):
        steps = [texts.t(
            "s2", self.language, i=1, a=self.dominoes[0][0], b=self.dominoes[0][1],
        )]
        for index in range(1, self.n):
            previous = self.dominoes[index - 1][1]
            left, right = self.dominoes[index]
            ok = 1 if previous == left else 0
            steps.append(texts.t(
                "s3", self.language, i=index + 1, a=left, b=right, prev=previous, ok=ok,
            ))
        steps.append(texts.t("s4", self.language, pips=self.pips, break_at=self.break_at))
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
