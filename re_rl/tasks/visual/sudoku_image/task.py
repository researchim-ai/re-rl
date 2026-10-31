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

class SudokuVisualTask(VisualTaskMixin, SudokuTask):
    """Судоку в виде картинки: назвать число в выделенной клетке."""

    TASK_TYPE = "sudoku_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         size=kwargs.get("size"),hints_ratio=kwargs.get("hints_ratio"))
        self._pick_target()
        self.description = self._descr(language)

    def _pick_target(self):
        from re_rl.tasks.math.logic.board_search_traces import sudoku
        empties = [(r,c) for r in range(self.size) for c in range(self.size) if self.puzzle[r][c] is None]
        if not empties:
            cell = (random.randrange(self.size),random.randrange(self.size))
            self.puzzle[cell[0]][cell[1]] = None
            empties = [cell]
        forced = []
        for r,c in empties:
            row = set(self._get_missing_in_row(self.puzzle,r))
            col = set(self._get_missing_in_col(self.puzzle,c))
            block = set(self._get_missing_in_block(self.puzzle,r//self.block_size,c//self.block_size))
            if len(row&col&block) == 1: forced.append((r,c))
        self.target = random.choice(forced or empties)
        r,c = self.target
        self.target_value = self.solution[r][c]
        # Add a public clue only when an actual alternative target value is found.
        while True:
            alternatives = sudoku(self.puzzle,forbidden=(r,c,self.target_value))
            if not alternatives: break
            witness = alternatives[0]
            differences = [(rr,cc) for rr in range(self.size) for cc in range(self.size)
                           if (rr,cc) != self.target and self.puzzle[rr][cc] is None
                           and witness[rr][cc] != self.solution[rr][cc]]
            if not differences: raise ValueError('ambiguous_target')
            rr,cc = random.choice(differences)
            self.puzzle[rr][cc] = self.solution[rr][cc]

    def render_image(self):
        cell = 46
        img = render_number_grid(self.puzzle, cell=cell, blanks=(None,),
                                 thick_every=self.block_size)
        draw = ImageDraw.Draw(img)
        r, c = self.target
        draw.rectangle([c * cell + 2, r * cell + 2, c * cell + cell - 2, r * cell + cell - 2],
                       outline=(220, 50, 47), width=3)
        draw.text((c * cell + cell * 0.36, r * cell + cell * 0.28), "?",
                  fill=(220, 50, 47), font=get_font(int(cell * 0.5)))
        return img

    def _descr(self, language):
        r, c = self.target
        return ((texts.t('s0', language, size=self.size, size_2=self.size, v2=r + 1, v3=c + 1)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.common('answer_line', self.language, answer=self.target_value)))]
        self.final_answer = str(self.target_value)

    def verify(self, prediction):
        fingerprint = (tuple(map(tuple,self.puzzle)),tuple(self.target))
        certificate = getattr(self,'_target_certificate',None)
        if certificate is None or certificate[:2] != fingerprint:
            try:
                self.solve()
            except ValueError:
                return 0.0
            certificate = self._target_certificate
        return U.verify_int(prediction,int(certificate[2]))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task
