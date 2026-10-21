"""Визуальные варианты существующих головоломок.

Логика генерации/решения полностью наследуется от текстовых задач — здесь только
рендеринг условия в изображение и формулировка, ссылающаяся на рисунок.

- ``sudoku_image``          — судоку: назвать число в выделенной клетке;
- ``sliding_puzzle_image``  — пятнашки: разрешимость / минимум ходов по картинке поля;
- ``arc_grid_image``        — ARC-индукция: примеры и тест — цветные сетки.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict
from PIL import ImageDraw
from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.sudoku_task import SudokuTask
from re_rl.tasks.math.logic.sliding_puzzle_task import SlidingPuzzleTask
from re_rl.tasks.math.logic.arc_induction_task import ARCGridInductionTask
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.visual._visual_utils import (
    VisualTaskMixin, render_number_grid, render_color_grid, get_font, ARC_PALETTE,
)

class ARCGridVisualTask(VisualTaskMixin, ARCGridInductionTask):
    """ARC-подобная индукция: примеры «вход→выход» и тест — цветные сетки."""

    TASK_TYPE = texts.literal('literals.s0')

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        from PIL import Image
        cell = 26
        pad = 16
        font = get_font(16)
        arrow_w = 28
        # размеры блоков
        rows = self.train + [(self.test_in, None)]
        cell_h = [len(g) for g, _ in rows]
        # ширина: input + arrow + output(или '?')
        def gw(g):
            return len(g[0]) * cell
        widths = []
        for gin, gout in rows:
            out = gout if gout is not None else self.test_out
            widths.append(gw(gin) + arrow_w + gw(out))
        W = max(widths) + 2 * pad + 40
        row_heights = [h * cell + pad for h in cell_h]
        H = sum(row_heights) + pad + 30
        img = Image.new("RGB", (W, H), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        y = pad + 20
        draw.text((pad, 4), texts.t('s2', self.language), fill=(0, 0, 0), font=font)
        for i, (gin, gout) in enumerate(rows):
            is_test = gout is None
            x = pad + 30
            render_color_grid(gin, ARC_PALETTE, cell=cell, origin=(x, y), img=img)
            ax = x + gw(gin)
            draw.text((ax + 6, y + gw(gin) * 0 + (len(gin) * cell) / 2 - 8), "→",
                      fill=(0, 0, 0), font=get_font(20))
            ox = ax + arrow_w
            if is_test:
                # рамка с вопросом вместо выхода
                ow, oh = len(self.test_out[0]) * cell, len(self.test_out) * cell
                draw.rectangle([ox, y, ox + ow, y + oh], outline=(220, 50, 47), width=2)
                draw.text((ox + ow / 2 - 6, y + oh / 2 - 10), "?", fill=(220, 50, 47),
                          font=get_font(22))
                draw.text((pad, y + oh / 2 - 8), texts.t('s4', self.language), fill=(220, 50, 47), font=font)
            else:
                render_color_grid(gout, ARC_PALETTE, cell=cell, origin=(ox, y), img=img)
            y += row_heights[i]
        return img

    def _descr_visual(self, language):
        ro, co = len(self.test_out), len(self.test_out[0])
        legend = "; ".join(f"{i}={name}" for i, name in enumerate(
            [texts.t('s5', language), texts.t('s6', language), texts.t('s7', language), texts.t('s8', language), texts.t('s9', language), texts.t('s10', language),
             texts.t('s11', language), texts.t('s12', language), texts.t('s13', language), texts.t('s14', language)][:self.colors]))
        if {"ru": True, "en": False}.get(language, False):
            return (texts.t('s3', language, legend=legend, ro=ro, co=co))
        legend_en = "; ".join(f"{i}={name}" for i, name in enumerate(
            ["black", "blue", "red", "green", "yellow", "grey",
             "pink", "orange", "cyan", "maroon"][:self.colors]))
        return (texts.t('s1', language, legend_en=legend_en, ro=ro, co=co))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
