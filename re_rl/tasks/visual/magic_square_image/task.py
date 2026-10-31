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

class MagicSquareVisualTask(VisualTaskMixin, MagicSquareTask):
    TASK_TYPE = texts.literal('literals.s1')

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        grid = [["?" if r * 3 + c in self.hidden else self.given[r * 3 + c]
                 for c in range(3)] for r in range(3)]
        return render_number_grid(grid, cell=64, blanks=())

    def _descr_visual(self, language):
        return ((texts.t('s0', language)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
