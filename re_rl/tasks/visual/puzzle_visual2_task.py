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


class GameOfLifeVisualTask(VisualTaskMixin, GameOfLifeTask):
    TASK_TYPE = "game_of_life_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        # 0 — мёртвая (белая), 1 — живая (чёрная)
        return render_color_grid(self.grid0, palette=[(255, 255, 255), (30, 30, 30)], cell=40)

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На рисунке — начальное поле игры «Жизнь» Конвея {self.r}×{self.c} (чёрные "
                 f"клетки — живые, белые — мёртвые; клетки вне поля считаются мёртвыми). Правила: "
                 f"живая клетка выживает при 2–3 живых соседях, мёртвая оживает при ровно 3. Каким "
                 f"будет поле через {self.k} шаг(а)? Выпишите все {self.r * self.c} клеток по "
                 f"строкам (1 — живая, 0 — мёртвая).") if ru else
                (f"The figure shows the initial board of Conway's Game of Life {self.r}×{self.c} "
                 f"(black cells are alive, white are dead; cells outside are dead). Rules: a live "
                 f"cell survives with 2–3 live neighbors, a dead cell is born with exactly 3. What "
                 f"is the board after {self.k} step(s)? List all {self.r * self.c} cells row by row "
                 f"(1 alive, 0 dead)."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task


class MagicSquareVisualTask(VisualTaskMixin, MagicSquareTask):
    TASK_TYPE = "magic_square_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        grid = [["?" if r * 3 + c in self.hidden else self.solution[r * 3 + c]
                 for c in range(3)] for r in range(3)]
        return render_number_grid(grid, cell=64, blanks=())

    def _descr_visual(self, language):
        ru = language == "ru"
        return (("На рисунке — магический квадрат 3×3 из чисел 1..9 (каждое по разу); суммы по "
                 "всем строкам, столбцам и двум диагоналям равны 15. Клетки со знаком «?» пусты. "
                 "Заполните пропуски и выпишите все 9 чисел по строкам сверху вниз.") if ru else
                ("The figure shows a 3×3 magic square using numbers 1..9 (each once); every row, "
                 "column and both diagonals sum to 15. Cells with «?» are empty. Fill the blanks "
                 "and list all 9 numbers row by row."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task


class GridNavigationVisualTask(VisualTaskMixin, GridNavigationTask):
    TASK_TYPE = "grid_navigation_image"
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
        ru = language == "ru"
        n = self.maze_n
        return ((f"На рисунке — лабиринт {n}×{n}: тёмные клетки — стены, светлые — свободны. Старт "
                 f"S (зелёная, левый верхний угол), цель G (красная, правый нижний). Разрешены ходы "
                 f"вверх/вниз/влево/вправо. Найдите длину кратчайшего пути (число шагов; -1, если "
                 f"пути нет).") if ru else
                (f"The figure shows an {n}×{n} maze: dark cells are walls, light cells are free. "
                 f"Start S (green, top-left), goal G (red, bottom-right). Moves: up/down/left/right. "
                 f"Find the shortest path length (number of steps; -1 if unreachable)."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
