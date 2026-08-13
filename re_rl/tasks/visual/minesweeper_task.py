"""Визуальный вариант «Сапёра»: поле рисуется как картинка (PIL).

Наследует логику от :class:`MinesweeperDeductionTask`: нужно определить, является
ли выделенная клетка миной. Ответ «мина»/«безопасно», `verify` без изменений.
"""

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.minesweeper_deduction_task import MinesweeperDeductionTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, get_font

_REVEALED = (225, 225, 225)
_HIDDEN = (150, 160, 170)
_TARGET = (255, 210, 120)
_NUMCOL = {0: (120, 120, 120), 1: (0, 0, 255), 2: (0, 128, 0), 3: (200, 0, 0),
           4: (0, 0, 128), 5: (128, 0, 0), 6: (0, 128, 128), 7: (0, 0, 0), 8: (90, 90, 90)}


class MinesweeperVisualTask(VisualTaskMixin, MinesweeperDeductionTask):
    TASK_TYPE = "minesweeper_image"
    CELL = 52

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        C, n = self.CELL, self.n
        img = Image.new("RGB", (n * C + 1, n * C + 1), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = get_font(int(C * 0.5))
        qfont = get_font(int(C * 0.55))
        for r in range(n):
            for c in range(n):
                x0, y0 = c * C, r * C
                is_target = (r, c) == self.target
                if (r, c) in self.revealed:
                    fill = _REVEALED
                elif is_target:
                    fill = _TARGET
                else:
                    fill = _HIDDEN
                draw.rectangle([x0, y0, x0 + C, y0 + C], fill=fill, outline=(80, 80, 80))
                if (r, c) in self.revealed:
                    v = self.number[(r, c)]
                    if v > 0:
                        s = str(v)
                        bb = draw.textbbox((0, 0), s, font=font)
                        draw.text((x0 + (C - (bb[2] - bb[0])) / 2, y0 + (C - (bb[3] - bb[1])) / 2 - bb[1]),
                                  s, fill=_NUMCOL.get(v, (0, 0, 0)), font=font)
                else:
                    s = "?"
                    col = (200, 0, 0) if is_target else (40, 40, 40)
                    bb = draw.textbbox((0, 0), s, font=qfont)
                    draw.text((x0 + (C - (bb[2] - bb[0])) / 2, y0 + (C - (bb[3] - bb[1])) / 2 - bb[1]),
                              s, fill=col, font=qfont)
                if is_target:
                    draw.rectangle([x0 + 2, y0 + 2, x0 + C - 2, y0 + C - 2],
                                   outline=(200, 0, 0), width=3)
        return img

    def _descr_visual(self, language):
        tr, tc = self.target
        ru = language == "ru"
        return ((f"На рисунке — поле «Сапёра» {self.n}×{self.n}. Числа в открытых клетках — сколько "
                 f"мин среди 8 соседей; серые клетки со знаком «?» скрыты. Целевая клетка обведена "
                 f"красным (строка {tr + 1}, столбец {tc + 1}). Является ли она миной? Ответьте "
                 f"«мина» или «безопасно».") if ru else
                (f"The figure shows a {self.n}×{self.n} Minesweeper board. Numbers in open cells are "
                 f"how many of the 8 neighbors are mines; grey '?' cells are hidden. The target cell "
                 f"is outlined in red (row {tr + 1}, column {tc + 1}). Is it a mine? Answer 'mine' or "
                 f"'safe'."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
