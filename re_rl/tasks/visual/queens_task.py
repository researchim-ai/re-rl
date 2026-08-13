"""Проверка расстановки ферзей по картинке (PIL).

На доске n×n расставлено по одному ферзю в каждой строке. Нужно определить,
корректна ли расстановка (никакие два ферзя не бьют друг друга). Ответ да/нет.
Данные считываются только с изображения.
"""

import random
from typing import Any, ClassVar, Dict, List

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, get_font
from re_rl.tasks.math.logic import _logic_utils as U

_LIGHT = (240, 217, 181)
_DARK = (181, 136, 99)


class QueensCheckVisualTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "queens_check_image"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 7}, 9: {"n": 8}, 10: {"n": 8},
    }
    CELL = 48

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _valid(self, cols: List[int]) -> bool:
        n = len(cols)
        if len(set(cols)) != n:
            return False
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                if abs(cols[r1] - cols[r2]) == abs(r1 - r2):
                    return False
        return True

    def _build(self):
        want_valid = random.random() < 0.5
        for _ in range(500):
            if want_valid:
                cols = self._random_valid()
                if cols is not None:
                    self.cols = cols
                    break
            else:
                cols = [random.randrange(self.n) for _ in range(self.n)]
                if not self._valid(cols):
                    self.cols = cols
                    break
        else:
            self.cols = self._random_valid() or [0] * self.n
        self.answer_bool = self._valid(self.cols)

    def _random_valid(self):
        n = self.n
        cols = [-1] * n
        used_c, d1, d2 = set(), set(), set()
        rows = list(range(n))

        def bt(r):
            if r == n:
                return True
            options = list(range(n))
            random.shuffle(options)
            for c in options:
                if c in used_c or (r - c) in d1 or (r + c) in d2:
                    continue
                cols[r] = c; used_c.add(c); d1.add(r - c); d2.add(r + c)
                if bt(r + 1):
                    return True
                used_c.discard(c); d1.discard(r - c); d2.discard(r + c)
            return False

        return cols if bt(0) else None

    def render_image(self):
        C, n = self.CELL, self.n
        img = Image.new("RGB", (n * C, n * C), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = get_font(int(C * 0.6))
        for r in range(n):
            for c in range(n):
                col = _DARK if (r + c) % 2 else _LIGHT
                draw.rectangle([c * C, r * C, c * C + C, r * C + C], fill=col)
        for r in range(n):
            c = self.cols[r]
            cx, cy = c * C + C / 2, r * C + C / 2
            pr = C * 0.34
            draw.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(30, 30, 30),
                         outline=(255, 255, 255), width=2)
            s = "Q"
            bb = draw.textbbox((0, 0), s, font=font)
            draw.text((cx - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - bb[1]), s,
                      fill=(255, 255, 255), font=font)
        return img

    def _descr(self, language):
        ru = language == "ru"
        return ((f"На доске {self.n}×{self.n} расставлено {self.n} ферзей (по одному в строке). "
                 f"Корректна ли расстановка, то есть никакие два ферзя не бьют друг друга (по "
                 f"вертикали, горизонтали или диагонали)? Ответьте да/нет.") if ru else
                (f"On an {self.n}×{self.n} board there are {self.n} queens (one per row). Is the "
                 f"placement valid, i.e. no two queens attack each other (same column, row or "
                 f"diagonal)? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        verdict = ("корректна" if self.answer_bool else "некорректна") if ru else (
            "valid" if self.answer_bool else "invalid")
        self.solution_steps = [
            ("Проверяем пары ферзей на общий столбец и диагонали (строки уже различны)." if ru else
             "Check queen pairs for a shared column or diagonal (rows already differ)."),
            (f"Расстановка {verdict}." if ru else f"The placement is {verdict}.")]
        self.final_answer = ("да" if self.answer_bool else "нет") if ru else (
            "yes" if self.answer_bool else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self.answer_bool))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task
