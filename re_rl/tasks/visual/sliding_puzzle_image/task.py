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

class SlidingPuzzleVisualTask(VisualTaskMixin, SlidingPuzzleTask):
    """Пятнашки в виде картинки поля."""

    TASK_TYPE = texts.literal('literals.s2')

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        super().__init__(task_type=task_type, language=language, detail_level=detail_level,
                         difficulty=difficulty, output_format=output_format,
                         reasoning_mode=reasoning_mode)
        self.description = self._descr_visual(language)

    def render_image(self):
        grid = [[self.board[r * self.n + c] for c in range(self.n)] for r in range(self.n)]
        return render_number_grid(grid, cell=56, blanks=(0,))

    def _descr_visual(self, language):
        goal = f"1..{self.n * self.n - 1}"
        if self.task_type == "solvable":
            return ((texts.t('s1', language, n=self.n, n_2=self.n, goal=goal)))
        return ((texts.t('s0', language, goal=goal)))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru", detail_level: int = 3,
                             difficulty: int = 5, reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
