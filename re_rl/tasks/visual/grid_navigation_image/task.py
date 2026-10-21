"""Ещё визуальные варианты головоломок (логика/verify наследуются от текстовых задач).

- ``game_of_life_image``  — начальное поле «Жизни» на картинке → каким станет через k шагов;
- ``magic_square_image``  — магический квадрат 3×3 с пропусками на картинке;
- ``grid_navigation_image`` — лабиринт: длина кратчайшего пути (start→goal).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

from PIL import Image, ImageDraw
from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.automata_sim_task import GameOfLifeTask
from re_rl.tasks.math.logic.magic_square_task import MagicSquareTask
from re_rl.tasks.math.logic.grid_navigation_task import GridNavigationTask
from re_rl.tasks.visual._visual_utils import (
    VisualTaskMixin, render_color_grid, render_number_grid, get_font,
)

class GridNavigationVisualTask(VisualTaskMixin, GridNavigationTask):
    TASK_TYPE = texts.literal('literals.s1')
    TASK_TYPES = ["maze"]  # визуализируем только лабиринт
    CELL = 40

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment, subtype="maze")
        self.description = self._descr_visual(language)

    def render_image(self):
        C, n = self.CELL, self.maze_n
        img = Image.new("RGB", (n * C, n * C), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = get_font(int(C * 0.4))
        for r in range(n):
            for c in range(n):
                fill = (40, 40, 40) if self.grid[r][c] else (245, 245, 245)
                draw.rectangle([c * C, r * C, c * C + C, r * C + C], fill=fill,
                               outline=(160, 160, 160))
        # старт (0,0) и цель (n-1,n-1)
        draw.rectangle([0, 0, C, C], fill=(120, 200, 120), outline=(0, 100, 0), width=2)
        draw.rectangle([(n - 1) * C, (n - 1) * C, n * C, n * C], fill=(230, 120, 120),
                       outline=(140, 0, 0), width=2)
        for (px, py, s) in [(0, 0, "S"), ((n - 1) * C, (n - 1) * C, "G")]:
            bb = draw.textbbox((0, 0), s, font=font)
            draw.text((px + (C - (bb[2] - bb[0])) / 2, py + (C - (bb[3] - bb[1])) / 2 - bb[1]),
                      s, fill=(0, 0, 0), font=font)
        return img

    def _descr_visual(self, language):
        n = self.maze_n
        return ((texts.t('s0', language, n=n, n_2=n)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
