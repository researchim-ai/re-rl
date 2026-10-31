from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, ClassVar

# Подключаем Z3
from z3 import Solver, Int, Distinct, sat

class FutoshikiTask(BaseTask):
    """
    Задача Futoshiki (неравенства) на N×N поле.
    
    Параметры сложности:
      - difficulty 1-2: поле 3x3
      - difficulty 3-4: поле 4x4
      - difficulty 5-6: поле 5x5
      - difficulty 7-8: поле 6x6
      - difficulty 9-10: поле 7x7
    """
    
    TASK_TYPE = "futoshiki"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 3, texts.literal('literals.s0'): 0.5},
        2: {"size": 3, texts.literal('literals.s1'): 0.7},
        3: {"size": 4, texts.literal('literals.s2'): 0.5},
        4: {"size": 4, texts.literal('literals.s3'): 0.7},
        5: {"size": 5, texts.literal('literals.s4'): 0.5},
        6: {"size": 5, texts.literal('literals.s5'): 0.7},
        7: {"size": 6, texts.literal('literals.s6'): 0.5},
        8: {"size": 6, texts.literal('literals.s7'): 0.7},
        9: {"size": 7, texts.literal('literals.s8'): 0.5},
        10: {"size": 7, texts.literal('literals.s9'): 0.7},
    }

    def __init__(
        self, 
        language="ru", 
        detail_level=5, 
        size=None, 
        num_inequalities=None,
        difficulty: int = None,
        output_format: str = "text",
        reasoning_mode: bool = False
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: сколько шагов (chain-of-thought) выводить
        :param size: размер поля (None -> случайно 4..5)
        :param num_inequalities: сколько неравенств генерировать (None -> случайно)
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода ('text' или 'latex')
        """
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if size is None:
                size = preset.get("size", 4)
            ratio = preset.get(texts.t('s10', language), 0.6)
            if num_inequalities is None:
                num_inequalities = int(size * size * ratio)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        if size is None:
            size = random.randint(4, 5)
        if type(size) is not int or not 1 <= size <= 9:
            raise ValueError("invalid_size")
        self.size = size
        
        if num_inequalities is None:
            num_inequalities = min(random.randint(size, size * 2),size*size*(size*size-size)//2)
        
        self.inequalities = self._generate_random_inequalities(num_inequalities)
        
        # The construction witness is a cache only; solve recomputes from inequalities.
        self.solution = self._generation_witness
        del self._generation_witness
        
        # Формируем текст постановки задачи
        problem_template = PROMPT_TEMPLATES["futoshiki"]["problem"][self.language]
        # Представим неравенства в читабельном виде
        ineq_str = ""
        for (r1,c1, r2,c2) in self.inequalities:
            ineq_str += f"({r1},{c1}) < ({r2},{c2})\n"
        
        problem_text = problem_template.format(
            size=self.size,
            inequalities=ineq_str
        )
        
        super().__init__(problem_text, language=self.language)
        self.reasoning_mode = reasoning_mode

    def _generate_random_inequalities(self, num_ineq):
        """
        Генерируем список случайных неравенств вида (r1,c1) < (r2,c2).
        Для Futoshiki обычно (r2,c2) — клетка, смежная с (r1,c1) 
        (по вертикали или горизонтали). 
        Но для простоты можно делать и не только смежные.
        """
        rows = random.sample(range(self.size),self.size)
        cols = random.sample(range(self.size),self.size)
        symbols = random.sample(range(1,self.size+1),self.size)
        witness = [[symbols[(r+c)%self.size] for c in cols] for r in rows]
        options = [(r,c,s,t) for r in range(self.size) for c in range(self.size)
                   for s in range(self.size) for t in range(self.size) if witness[r][c] < witness[s][t]]
        if type(num_ineq) is not int or not 0 <= num_ineq <= len(options):
            raise ValueError('invalid_num_inequalities')
        self._generation_witness = witness
        return random.sample(options,num_ineq)

    def get_task_type(self):
        
        return "futoshiki"


    def _solve_with_z3(self):
        """
        Строим модель Z3:
          - Определяем переменные cell[r][c] (Int)
          - Добавляем ограничения: 1 <= cell[r][c] <= size
          - distinct по каждой строке и столбцу
          - неравенства
        Возвращаем решение в виде двумерного массива (size×size).
        Если unsat, вернём None (или бросим исключение).
        """
        s = Solver()
        
        # Создадим матрицу Z3-переменных: cell[r][c]
        self.cells = [
            [Int(f"cell_{r}_{c}") for c in range(self.size)]
            for r in range(self.size)
        ]
        
        # Базовые ограничения: 1 <= cell[r][c] <= size
        for r in range(self.size):
            for c in range(self.size):
                s.add(self.cells[r][c] >= 1, self.cells[r][c] <= self.size)
        
        # Уникальность в каждой строке
        for r in range(self.size):
            s.add(Distinct(*self.cells[r]))
        
        # Уникальность в каждом столбце
        for c in range(self.size):
            col_vars = [self.cells[r][c] for r in range(self.size)]
            s.add(Distinct(*col_vars))
        
        # Неравенства
        for (r1,c1, r2,c2) in self.inequalities:
            s.add(self.cells[r1][c1] < self.cells[r2][c2])
        
        # Попытаемся найти решение
        result = s.check()
        if result != sat:
            # Solver did not return a satisfying model.
            # Для примера: пусть возвращает None
            return None
        
        m = s.model()
        # Формируем итоговую матрицу
        solution_matrix = [[0]*self.size for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                solution_matrix[r][c] = m[self.cells[r][c]].as_long()
        return solution_matrix

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = []
        if self.solution is None:
            self.final_answer = texts.t('s12',self.language)
        else:
            self.final_answer = PROMPT_TEMPLATES['futoshiki']['final_answer'][self.language].format(grid_repr=self._format_solution())

    def verify(self,prediction):
        from re_rl.tasks.math.logic import _logic_utils as U
        from re_rl.tasks.math.logic.puzzle_inference import futoshiki
        text = U.clean(prediction)
        if text in (texts.t('s12','ru'),texts.t('s12','en')):
            return float(futoshiki(self.size,self.inequalities,[]) is None)
        import re
        for language in ('ru','en'):
            header = PROMPT_TEMPLATES['futoshiki']['final_answer'][language].split('{grid_repr}')[0]
            if text.startswith(header):text = text[len(header):]
        if not re.fullmatch(r'[\s\[\],0-9]+',text):return 0.0
        values = list(map(int,re.findall(r'[0-9]+',text)))
        if len(values) != self.size*self.size:return 0.0
        grid = [values[r*self.size:(r+1)*self.size] for r in range(self.size)]
        expected = set(range(1,self.size+1))
        if any(set(row) != expected for row in grid) or any({grid[r][c] for r in range(self.size)} != expected for c in range(self.size)):
            return 0.0
        return float(all(grid[r][c] < grid[s][t] for r,c,s,t in self.inequalities))

    def _format_solution(self):
        if self.solution is None:
            return ""
        lines = []
        for r in range(self.size):
            line = " ".join(str(self.solution[r][c]) for c in range(self.size))
            lines.append(line)
        return "\n".join(lines)

    def get_result(self):
        return super().get_result()
