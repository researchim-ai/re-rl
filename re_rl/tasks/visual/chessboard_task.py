"""Шахматная доска с фигурами (визуальная задача, PIL).

Подтипы:
- ``total``   — сколько всего фигур на доске;
- ``on_dark`` — сколько фигур стоит на тёмных клетках;
- ``on_light``— сколько фигур стоит на светлых клетках.

Фигуры изображаются как кружки; задача — визуальный подсчёт.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin
from re_rl.tasks.math.logic import _logic_utils as U

_LIGHT = (240, 217, 181)
_DARK = (181, 136, 99)


class ChessboardCountTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "chessboard_count"
    TASK_TYPES = ["total", "on_dark", "on_light"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 3}, 2: {"k": 4}, 3: {"k": 5}, 4: {"k": 6}, 5: {"k": 8},
        6: {"k": 10}, 7: {"k": 12}, 8: {"k": 14}, 9: {"k": 16}, 10: {"k": 20},
    }
    N = 8
    CELL = 44

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.k = min(int(p["k"]), self.N * self.N)
        cells = random.sample([(r, c) for r in range(self.N) for c in range(self.N)], self.k)
        self.pieces: List[Tuple[int, int]] = cells
        dark = sum(1 for (r, c) in cells if (r + c) % 2 == 1)
        if self.task_type == "on_dark":
            self.answer = dark
        elif self.task_type == "on_light":
            self.answer = self.k - dark
        else:
            self.answer = self.k
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def render_image(self):
        C, N = self.CELL, self.N
        img = Image.new("RGB", (N * C, N * C), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for r in range(N):
            for c in range(N):
                col = _DARK if (r + c) % 2 == 1 else _LIGHT
                draw.rectangle([c * C, r * C, c * C + C, r * C + C], fill=col)
        pr = C * 0.32
        for (r, c) in self.pieces:
            cx, cy = c * C + C / 2, r * C + C / 2
            draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr],
                         fill=(30, 30, 30), outline=(255, 255, 255), width=2)
        return img

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "on_dark":
            return ("На шахматной доске расставлены фигуры (тёмные кружки). Сколько фигур стоит "
                    "на тёмных клетках?" if ru else
                    "Pieces (dark circles) are placed on a chessboard. How many stand on dark "
                    "squares?")
        if self.task_type == "on_light":
            return ("На шахматной доске расставлены фигуры (тёмные кружки). Сколько фигур стоит "
                    "на светлых клетках?" if ru else
                    "Pieces (dark circles) are placed on a chessboard. How many stand on light "
                    "squares?")
        return ("На шахматной доске расставлены фигуры (тёмные кружки). Сколько всего фигур на "
                "доске?" if ru else
                "Pieces (dark circles) are placed on a chessboard. How many pieces are there in "
                "total?")

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Подсчитываем нужные фигуры на доске." if ru else "Count the relevant pieces."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
