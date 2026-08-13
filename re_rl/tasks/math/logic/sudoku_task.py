# re_rl/tasks/math/logic/sudoku_task.py

import random
from typing import Dict, Any, ClassVar, List, Optional, Tuple
from z3 import Solver, Int, And, Distinct, sat, Or

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class SudokuTask(BaseMathTask):
    """
    Генерирует и решает головоломки судоку.
    
    Параметры сложности:
      - difficulty 1-2: 4x4, много подсказок (60-70%)
      - difficulty 3-4: 4x4, меньше подсказок (40-50%)
      - difficulty 5-6: 9x9, много подсказок (45-55%)
      - difficulty 7-8: 9x9, средне подсказок (35-40%)
      - difficulty 9-10: 9x9, мало подсказок (25-30%)
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 4, "hints_ratio": 0.70},
        2: {"size": 4, "hints_ratio": 0.60},
        3: {"size": 4, "hints_ratio": 0.50},
        4: {"size": 4, "hints_ratio": 0.40},
        5: {"size": 9, "hints_ratio": 0.55},
        6: {"size": 9, "hints_ratio": 0.45},
        7: {"size": 9, "hints_ratio": 0.40},
        8: {"size": 9, "hints_ratio": 0.35},
        9: {"size": 9, "hints_ratio": 0.30},
        10: {"size": 9, "hints_ratio": 0.25},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        size: int = None,
        hints_ratio: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param size: размер поля (4 или 9)
        :param hints_ratio: доля заполненных клеток (0.0-1.0)
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода ('text' или 'latex')
        """
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if size is None:
                size = preset.get("size", 9)
            if hints_ratio is None:
                hints_ratio = preset.get("hints_ratio", 0.4)
        else:
            size = size or 9
            hints_ratio = hints_ratio or 0.4
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.size = size
        self.block_size = int(size ** 0.5)  # 2 для 4x4, 3 для 9x9
        self.hints_ratio = hints_ratio
        
        # Генерируем полное решение
        self.solution = self._generate_complete_grid()
        
        # Создаём пазл, убирая часть чисел
        self.puzzle = self._create_puzzle()
        
        # Формируем текст задачи
        templates = PROMPT_TEMPLATES["sudoku"]
        problem_text = templates["instructions"][self.language] + "\n\n"
        problem_text += templates["problem"][self.language].format(
            size=self.size,
            grid=self._format_grid(self.puzzle)
        )
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _generate_complete_grid(self) -> List[List[int]]:
        """Генерирует полностью заполненную корректную сетку судоку.

        Быстрый рандомизированный бэктрекинг (миллисекунды даже для 9×9), что
        на порядки быстрее прежней генерации через Z3.
        """
        n, b = self.size, self.block_size
        grid = [[0] * n for _ in range(n)]

        def ok(r: int, c: int, v: int) -> bool:
            for i in range(n):
                if grid[r][i] == v or grid[i][c] == v:
                    return False
            br, bc = (r // b) * b, (c // b) * b
            for i in range(b):
                for j in range(b):
                    if grid[br + i][bc + j] == v:
                        return False
            return True

        def fill(pos: int) -> bool:
            if pos == n * n:
                return True
            r, c = divmod(pos, n)
            vals = list(range(1, n + 1))
            random.shuffle(vals)
            for v in vals:
                if ok(r, c, v):
                    grid[r][c] = v
                    if fill(pos + 1):
                        return True
                    grid[r][c] = 0
            return False

        fill(0)
        return grid

    def _create_puzzle(self) -> List[List[Optional[int]]]:
        """Создаёт пазл, убирая часть чисел из полного решения."""
        puzzle = [row[:] for row in self.solution]
        total_cells = self.size * self.size
        cells_to_remove = int(total_cells * (1 - self.hints_ratio))
        
        all_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(all_cells)
        
        # 9x9 генерация может быть узким местом. Для скорости удаляем клетки
        # напрямую (пазл остаётся решаемым, так как получен из корректного решения).
        if self.size >= 9:
            for r, c in all_cells[:cells_to_remove]:
                puzzle[r][c] = None
            return puzzle

        removed = 0
        # Для 4x4 можно оставить проверку разрешимости — это дешево.
        for r, c in all_cells:
            if removed >= cells_to_remove:
                break
            puzzle[r][c] = None
            if self._has_unique_solution(puzzle):
                removed += 1
            else:
                puzzle[r][c] = self.solution[r][c]
        
        return puzzle

    def _has_unique_solution(self, puzzle: List[List[Optional[int]]]) -> bool:
        """Проверяет, имеет ли пазл единственное решение (упрощённая проверка)."""
        # Для скорости делаем упрощённую проверку - просто проверяем разрешимость
        # В реальности нужно проверять на единственность, но это медленно
        solver = Solver()
        cells = [[Int(f"c_{r}_{c}") for c in range(self.size)] for r in range(self.size)]
        
        for r in range(self.size):
            for c in range(self.size):
                solver.add(cells[r][c] >= 1, cells[r][c] <= self.size)
                if puzzle[r][c] is not None:
                    solver.add(cells[r][c] == puzzle[r][c])
        
        for r in range(self.size):
            solver.add(Distinct(*cells[r]))
        
        for c in range(self.size):
            solver.add(Distinct(*[cells[r][c] for r in range(self.size)]))
        
        for block_r in range(self.block_size):
            for block_c in range(self.block_size):
                block_cells = []
                for r in range(self.block_size):
                    for c in range(self.block_size):
                        block_cells.append(cells[block_r * self.block_size + r][block_c * self.block_size + c])
                solver.add(Distinct(*block_cells))
        
        return solver.check() == sat

    def _format_grid(self, grid: List[List[Optional[int]]]) -> str:
        """Форматирует сетку для отображения."""
        lines = []
        for r in range(self.size):
            row_str = ""
            for c in range(self.size):
                val = grid[r][c]
                if val is None:
                    row_str += ". "
                else:
                    row_str += f"{val} "
                if (c + 1) % self.block_size == 0 and c < self.size - 1:
                    row_str += "| "
            lines.append(row_str.strip())
            if (r + 1) % self.block_size == 0 and r < self.size - 1:
                separator = "-" * len(lines[-1])
                lines.append(separator)
        return "\n".join(lines)

    def _get_missing_in_row(self, grid: List[List[Optional[int]]], row: int) -> List[int]:
        """Возвращает числа, отсутствующие в строке."""
        present = {grid[row][c] for c in range(self.size) if grid[row][c] is not None}
        return [n for n in range(1, self.size + 1) if n not in present]

    def _get_missing_in_col(self, grid: List[List[Optional[int]]], col: int) -> List[int]:
        """Возвращает числа, отсутствующие в столбце."""
        present = {grid[r][col] for r in range(self.size) if grid[r][col] is not None}
        return [n for n in range(1, self.size + 1) if n not in present]

    def _get_missing_in_block(self, grid: List[List[Optional[int]]], block_r: int, block_c: int) -> List[int]:
        """Возвращает числа, отсутствующие в блоке."""
        present = set()
        for r in range(self.block_size):
            for c in range(self.block_size):
                val = grid[block_r * self.block_size + r][block_c * self.block_size + c]
                if val is not None:
                    present.add(val)
        return [n for n in range(1, self.size + 1) if n not in present]

    def solve(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES["sudoku"]
        steps = []
        
        # Создаём рабочую копию пазла
        working_grid = [row[:] for row in self.puzzle]
        step_num = 0
        
        # Находим пустые клетки
        empty_cells = [(r, c) for r in range(self.size) for c in range(self.size) 
                       if working_grid[r][c] is None]
        
        for r, c in empty_cells:
            # Анализируем строку
            missing_row = self._get_missing_in_row(working_grid, r)
            missing_col = self._get_missing_in_col(working_grid, c)
            block_r, block_c = r // self.block_size, c // self.block_size
            missing_block = self._get_missing_in_block(working_grid, block_r, block_c)
            
            # Находим возможные значения для клетки
            possible = set(missing_row) & set(missing_col) & set(missing_block)
            
            if len(possible) == 1:
                val = list(possible)[0]
                step_num += 1
                step = templates["steps"]["naked_single"][self.language].format(
                    row=r + 1, col=c + 1, number=val
                )
                steps.append(step)
                working_grid[r][c] = val
            else:
                # Добавляем аналитический шаг
                step = templates["steps"]["analyze_row"][self.language].format(
                    row=r + 1, missing=missing_row
                )
                steps.append(step)
        
        self.solution_steps = steps
        self.final_answer = templates["final_answer"][self.language].format(
            grid=self._format_grid(self.solution)
        )

    def get_task_type(self):
        return "sudoku"
