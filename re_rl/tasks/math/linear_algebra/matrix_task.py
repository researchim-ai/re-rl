# re_rl/tasks/matrix_task.py

"""
MatrixTask — задачи с матрицами.

Поддерживаемые типы:
- determinant: вычисление определителя
- inverse: обратная матрица
- multiplication: умножение матриц
- transpose: транспонирование
- rank: ранг матрицы
- eigenvalues: собственные значения
- trace: след матрицы
- add: сложение матриц
- scalar_mult: умножение на скаляр
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass
import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class MatrixTask(BaseMathTask):
    """Задачи с матрицами."""
    
    TASK_TYPES = [
        "determinant", "inverse", "multiplication", "transpose",
        "rank", "eigenvalues", "trace", "add", "scalar_mult"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_size": 2, "max_value": 5},
        2: {"max_size": 2, "max_value": 10},
        3: {"max_size": 3, "max_value": 5},
        4: {"max_size": 3, "max_value": 10},
        5: {"max_size": 3, "max_value": 15},
        6: {"max_size": 4, "max_value": 10},
        7: {"max_size": 4, "max_value": 15},
        8: {"max_size": 4, "max_value": 20},
        9: {"max_size": 5, "max_value": 10},
        10: {"max_size": 5, "max_value": 20},
    }
    
    def __init__(
        self,
        task_type: str = "determinant",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.kwargs = kwargs
        self._output_format = output_format
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_size = kwargs.get("max_size", preset.get("max_size", 3))
        self.max_value = kwargs.get("max_value", preset.get("max_value", 10))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_random_matrix(self, rows: int, cols: int) -> List[List[int]]:
        """Генерирует случайную матрицу."""
        return [[random.randint(-self.max_value, self.max_value) for _ in range(cols)] for _ in range(rows)]
    
    def _matrix_to_str(self, matrix: List[List[int]]) -> str:
        """Преобразует матрицу в строковое представление."""
        rows = []
        for row in matrix:
            rows.append("[" + ", ".join(map(str, row)) + "]")
        return "[" + ", ".join(rows) + "]"
    
    def _matrix_to_pretty_str(self, matrix: List[List[int]]) -> str:
        """Преобразует матрицу в красивое представление."""
        rows = []
        for row in matrix:
            rows.append("│ " + " ".join(f"{x:4}" for x in row) + " │")
        return "\n".join(rows)
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type in ["determinant", "inverse", "eigenvalues", "trace"]:
            # Квадратная матрица
            size = self.kwargs.get("size", random.randint(2, self.max_size))
            self.matrix = self.kwargs.get("matrix", self._generate_random_matrix(size, size))
            
            # Для обратной матрицы гарантируем ненулевой определитель
            if self.task_type == "inverse":
                while abs(self._det(self.matrix)) < 0.001:
                    self.matrix = self._generate_random_matrix(size, size)
        
        elif self.task_type == "multiplication":
            # Две матрицы для умножения
            m = self.kwargs.get("m", random.randint(2, self.max_size))
            n = self.kwargs.get("n", random.randint(2, self.max_size))
            p = self.kwargs.get("p", random.randint(2, self.max_size))
            self.matrix_a = self.kwargs.get("matrix_a", self._generate_random_matrix(m, n))
            self.matrix_b = self.kwargs.get("matrix_b", self._generate_random_matrix(n, p))
        
        elif self.task_type == "transpose":
            rows = self.kwargs.get("rows", random.randint(2, self.max_size))
            cols = self.kwargs.get("cols", random.randint(2, self.max_size))
            self.matrix = self.kwargs.get("matrix", self._generate_random_matrix(rows, cols))
        
        elif self.task_type == "rank":
            rows = self.kwargs.get("rows", random.randint(2, self.max_size))
            cols = self.kwargs.get("cols", random.randint(2, self.max_size))
            self.matrix = self.kwargs.get("matrix", self._generate_random_matrix(rows, cols))
        
        elif self.task_type == "add":
            size = self.kwargs.get("size", random.randint(2, self.max_size))
            self.matrix_a = self.kwargs.get("matrix_a", self._generate_random_matrix(size, size))
            self.matrix_b = self.kwargs.get("matrix_b", self._generate_random_matrix(size, size))
        
        elif self.task_type == "scalar_mult":
            size = self.kwargs.get("size", random.randint(2, self.max_size))
            self.matrix = self.kwargs.get("matrix", self._generate_random_matrix(size, size))
            self.scalar = self.kwargs.get("scalar", random.randint(-5, 5))
            while self.scalar == 0:
                self.scalar = random.randint(-5, 5)
    
    def _det(self, matrix: List[List[int]]) -> float:
        """Вычисляет определитель матрицы."""
        return float(np.linalg.det(np.array(matrix)))
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("matrix", {}).get("problem", {})
        
        if self.task_type == "determinant":
            template = templates.get("determinant", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "inverse":
            template = templates.get("inverse", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "multiplication":
            template = templates.get("multiplication", {}).get(self.language, "")
            return template.format(
                matrix_a=self._matrix_to_pretty_str(self.matrix_a),
                matrix_b=self._matrix_to_pretty_str(self.matrix_b)
            )
        
        elif self.task_type == "transpose":
            template = templates.get("transpose", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "rank":
            template = templates.get("rank", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "eigenvalues":
            template = templates.get("eigenvalues", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "trace":
            template = templates.get("trace", {}).get(self.language, "")
            return template.format(matrix=self._matrix_to_pretty_str(self.matrix))
        
        elif self.task_type == "add":
            template = templates.get("add", {}).get(self.language, "")
            return template.format(
                matrix_a=self._matrix_to_pretty_str(self.matrix_a),
                matrix_b=self._matrix_to_pretty_str(self.matrix_b)
            )
        
        elif self.task_type == "scalar_mult":
            template = templates.get("scalar_mult", {}).get(self.language, "")
            return template.format(scalar=self.scalar, matrix=self._matrix_to_pretty_str(self.matrix))
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("matrix", {}).get("steps", {})
        
        if self.task_type == "determinant":
            self._solve_determinant(steps_templates)
        elif self.task_type == "inverse":
            self._solve_inverse(steps_templates)
        elif self.task_type == "multiplication":
            self._solve_multiplication(steps_templates)
        elif self.task_type == "transpose":
            self._solve_transpose(steps_templates)
        elif self.task_type == "rank":
            self._solve_rank(steps_templates)
        elif self.task_type == "eigenvalues":
            self._solve_eigenvalues(steps_templates)
        elif self.task_type == "trace":
            self._solve_trace(steps_templates)
        elif self.task_type == "add":
            self._solve_add(steps_templates)
        elif self.task_type == "scalar_mult":
            self._solve_scalar_mult(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_determinant(self, templates):
        """Вычисление определителя."""
        n = len(self.matrix)
        
        if n == 2:
            a11, a12 = self.matrix[0]
            a21, a22 = self.matrix[1]
            det = a11 * a22 - a12 * a21
            
            template = templates.get("det_2x2", {}).get(self.language, "")
            self.solution_steps.append(template.format(
                step=1, a11=a11, a12=a12, a21=a21, a22=a22, result=det
            ))
        else:
            # Разложение по первой строке
            det = round(self._det(self.matrix))
            
            template = templates.get("det_expansion", {}).get(self.language, "")
            row_col = "строке" if self.language == "ru" else "row"
            self.solution_steps.append(template.format(
                step=1, row_col=row_col, index=1, expansion="...", result=det
            ))
        
        self.final_answer = str(round(self._det(self.matrix)))
    
    def _solve_inverse(self, templates):
        """Обратная матрица."""
        matrix_np = np.array(self.matrix, dtype=float)
        det = np.linalg.det(matrix_np)
        
        misc = PROMPT_TEMPLATES.get("matrix", {}).get("misc", {})
        
        if abs(det) < 0.001:
            self.final_answer = misc.get("singular_matrix", {}).get(self.language, "Matrix is singular")
            return
        
        inverse = np.linalg.inv(matrix_np)
        
        template = templates.get("inverse_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1))
        
        det_step = misc.get("det_step", {}).get(self.language, "")
        self.solution_steps.append(det_step.format(det=f"{det:.4f}"))
        
        # Форматируем ответ
        result_str = "\n".join([
            "[" + ", ".join(f"{x:.4f}" for x in row) + "]"
            for row in inverse.tolist()
        ])
        self.final_answer = result_str
    
    def _solve_multiplication(self, templates):
        """Умножение матриц."""
        A = np.array(self.matrix_a)
        B = np.array(self.matrix_b)
        C = np.dot(A, B)
        
        # Показываем элемент C[0][0]
        template = templates.get("multiplication_element", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, i=1, j=1, result=C[0][0]
        ))
        
        result_str = self._matrix_to_str(C.tolist())
        self.final_answer = result_str
    
    def _solve_transpose(self, templates):
        """Транспонирование."""
        matrix_np = np.array(self.matrix)
        transposed = matrix_np.T
        
        template = templates.get("transpose_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, i=1, j=1, result=transposed[0][0]))
        
        self.final_answer = self._matrix_to_str(transposed.tolist())
    
    def _solve_rank(self, templates):
        """Ранг матрицы."""
        matrix_np = np.array(self.matrix, dtype=float)
        rank = np.linalg.matrix_rank(matrix_np)
        
        misc = PROMPT_TEMPLATES.get("matrix", {}).get("misc", {})
        
        step1 = misc.get("reduce_to_echelon", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        step2 = misc.get("count_nonzero_rows", {}).get(self.language, "")
        self.solution_steps.append(step2.format(rank=rank))
        
        self.final_answer = str(rank)
    
    def _solve_eigenvalues(self, templates):
        """Собственные значения."""
        matrix_np = np.array(self.matrix, dtype=float)
        eigenvalues = np.linalg.eigvals(matrix_np)
        
        template = templates.get("eigenvalue_char_poly", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, poly="det(A - λI) = 0"))
        
        # Форматируем собственные значения
        eigenvalues_str = ", ".join([f"{ev:.4f}" for ev in eigenvalues])
        
        template2 = templates.get("eigenvalue_roots", {}).get(self.language, "")
        self.solution_steps.append(template2.format(step=2, eigenvalues=eigenvalues_str))
        
        self.final_answer = eigenvalues_str
    
    def _solve_trace(self, templates):
        """След матрицы."""
        trace = sum(self.matrix[i][i] for i in range(len(self.matrix)))
        diag_str = " + ".join([str(self.matrix[i][i]) for i in range(len(self.matrix))])
        
        misc = PROMPT_TEMPLATES.get("matrix", {}).get("misc", {})
        step = misc.get("trace_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(diag_str=diag_str, trace=trace))
        
        self.final_answer = str(trace)
    
    def _solve_add(self, templates):
        """Сложение матриц."""
        A = np.array(self.matrix_a)
        B = np.array(self.matrix_b)
        C = A + B
        
        misc = PROMPT_TEMPLATES.get("matrix", {}).get("misc", {})
        step = misc.get("add_elements", {}).get(self.language, "")
        self.solution_steps.append(step)
        
        self.final_answer = self._matrix_to_str(C.tolist())
    
    def _solve_scalar_mult(self, templates):
        """Умножение на скаляр."""
        matrix_np = np.array(self.matrix)
        result = self.scalar * matrix_np
        
        misc = PROMPT_TEMPLATES.get("matrix", {}).get("misc", {})
        step = misc.get("scalar_multiply", {}).get(self.language, "")
        self.solution_steps.append(step.format(scalar=self.scalar))
        
        self.final_answer = self._matrix_to_str(result.tolist())
    
    def get_task_type(self) -> str:
        return "matrix"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу с матрицами."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
