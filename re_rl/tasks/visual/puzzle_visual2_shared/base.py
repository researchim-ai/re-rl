"""Ещё визуальные варианты головоломок (логика/verify наследуются от текстовых задач).

- ``game_of_life_image``  — начальное поле «Жизни» на картинке → каким станет через k шагов;
- ``magic_square_image``  — магический квадрат 3×3 с пропусками на картинке;
- ``grid_navigation_image`` — лабиринт: длина кратчайшего пути (start→goal).
"""

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.automata_sim_task import GameOfLifeTask
from re_rl.tasks.math.logic.magic_square_task import MagicSquareTask
from re_rl.tasks.math.logic.grid_navigation_task import GridNavigationTask
from re_rl.tasks.visual._visual_utils import (
    VisualTaskMixin, render_color_grid, render_number_grid, get_font,
)









