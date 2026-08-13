"""Визуальные варианты существующих головоломок.

Логика генерации/решения полностью наследуется от текстовых задач — здесь только
рендеринг условия в изображение и формулировка, ссылающаяся на рисунок.

- ``sudoku_image``          — судоку: назвать число в выделенной клетке;
- ``sliding_puzzle_image``  — пятнашки: разрешимость / минимум ходов по картинке поля;
- ``arc_grid_image``        — ARC-индукция: примеры и тест — цветные сетки.
"""

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
                         output_format=output_format, reasoning_mode=reasoning_mode)
        self._pick_target()
        self.description = self._descr(language)

    def _pick_target(self):
        empties = [(r, c) for r in range(self.size) for c in range(self.size)
                   if self.puzzle[r][c] is None]
        # предпочитаем клетку с единственным кандидатом (ответ гарантированно однозначен)
        forced = []
        for r, c in empties:
            mr = set(self._get_missing_in_row(self.puzzle, r))
            mc = set(self._get_missing_in_col(self.puzzle, c))
            mb = set(self._get_missing_in_block(self.puzzle, r // self.block_size,
                                                c // self.block_size))
            if len(mr & mc & mb) == 1:
                forced.append((r, c))
        self.target = random.choice(forced) if forced else random.choice(empties)
        self.target_value = self.solution[self.target[0]][self.target[1]]

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
        ru = language == "ru"
        return ((f"На рисунке — судоку {self.size}×{self.size}; пустые клетки обозначены точкой. "
                 f"Какое число должно стоять в выделенной красным клетке "
                 f"(строка {r + 1}, столбец {c + 1})?") if ru else
                (f"The figure shows a {self.size}×{self.size} Sudoku; empty cells are dots. "
                 f"Which number belongs in the red-highlighted cell "
                 f"(row {r + 1}, column {c + 1})?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Единственное число, допустимое в строке, столбце и блоке для этой клетки." if ru
             else "The only number allowed by the row, column and block for that cell."),
            (f"Ответ: {self.target_value}." if ru else f"Answer: {self.target_value}.")]
        self.final_answer = str(self.target_value)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.target_value))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task


class SlidingPuzzleVisualTask(VisualTaskMixin, SlidingPuzzleTask):
    """Пятнашки в виде картинки поля."""

    TASK_TYPE = "sliding_puzzle_image"

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
        ru = language == "ru"
        goal = f"1..{self.n * self.n - 1}"
        if self.task_type == "solvable":
            return ((f"На рисунке — расстановка пятнашек {self.n}×{self.n} (пустая клетка не "
                     f"подписана). Цель — упорядочить плитки {goal} с пустой клеткой в правом "
                     f"нижнем углу. Разрешима ли эта расстановка? (да/нет)") if ru else
                    (f"The figure shows a {self.n}×{self.n} sliding puzzle (the blank cell is "
                     f"empty). Goal: tiles {goal} in order with the blank at the bottom-right. "
                     f"Is this configuration solvable? (yes/no)"))
        return ((f"На рисунке — расстановка пятнашек 3×3 (пустая клетка не подписана). Цель — "
                 f"упорядочить плитки {goal} с пустой клеткой снизу справа. За минимальное число "
                 f"ходов приведите поле к цели. Сколько ходов минимально?") if ru else
                (f"The figure shows a 3×3 sliding puzzle (the blank cell is empty). Goal: tiles "
                 f"{goal} in order with the blank at the bottom-right. What is the minimum number "
                 f"of moves to reach the goal?"))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru", detail_level: int = 3,
                             difficulty: int = 5, reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task


class ARCGridVisualTask(VisualTaskMixin, ARCGridInductionTask):
    """ARC-подобная индукция: примеры «вход→выход» и тест — цветные сетки."""

    TASK_TYPE = "arc_grid_image"

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
        draw.text((pad, 4), "Примеры (вход → выход), затем тест:", fill=(0, 0, 0), font=font)
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
                draw.text((pad, y + oh / 2 - 8), "тест", fill=(220, 50, 47), font=font)
            else:
                render_color_grid(gout, ARC_PALETTE, cell=cell, origin=(ox, y), img=img)
            y += row_heights[i]
        return img

    def _descr_visual(self, language):
        ru = language == "ru"
        ro, co = len(self.test_out), len(self.test_out[0])
        legend = "; ".join(f"{i}={name}" for i, name in enumerate(
            ["чёрный", "синий", "красный", "зелёный", "жёлтый", "серый",
             "розовый", "оранжевый", "голубой", "бордовый"][:self.colors]))
        if ru:
            return (f"На рисунке несколько примеров «вход → выход», преобразованных по ОДНОМУ "
                    f"скрытому правилу (клетки раскрашены по цифрам-цветам: {legend}). Для "
                    f"тестового входа (последняя строка) выход скрыт. Определите правило и "
                    f"выпишите выходную сетку ({ro}×{co}) — все числа-цвета по строкам.")
        legend_en = "; ".join(f"{i}={name}" for i, name in enumerate(
            ["black", "blue", "red", "green", "yellow", "grey",
             "pink", "orange", "cyan", "maroon"][:self.colors]))
        return (f"The figure shows several input→output examples transformed by ONE hidden rule "
                f"(cells colored by number: {legend_en}). For the test input (last row) the "
                f"output is hidden. Infer the rule and output the grid ({ro}×{co}) — all color "
                f"numbers row by row.")

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
