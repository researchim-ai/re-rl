# re_rl/tasks/system_linear_task.py

import random
import numpy as np
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, ClassVar, Optional, List

class SystemLinearTask(BaseMathTask):
    """
    Решает систему линейных уравнений методом Крамера.
    
    Параметры сложности:
      - difficulty 1-3: система 2x2
      - difficulty 4-6: система 3x3
      - difficulty 7-8: система 4x4
      - difficulty 9-10: система 5x5
      
    detail_level определяет количество шагов решения.
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 2, "max_coef": 5},
        2: {"size": 2, "max_coef": 10},
        3: {"size": 2, "max_coef": 10},
        4: {"size": 3, "max_coef": 5},
        5: {"size": 3, "max_coef": 10},
        6: {"size": 3, "max_coef": 10},
        7: {"size": 4, "max_coef": 5},
        8: {"size": 4, "max_coef": 10},
        9: {"size": 5, "max_coef": 5},
        10: {"size": 5, "max_coef": 10},
    }
    
    def __init__(
        self, 
        matrix: Optional[List[List[float]]] = None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        size: int = 2,
        max_coef: int = 10
    ):
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            size = preset.get("size", size)
            max_coef = preset.get("max_coef", max_coef)
        
        # Генерируем матрицу, если не задана
        if matrix is None:
            matrix = self._generate_matrix(size, max_coef)
        
        self.matrix = np.array(matrix, dtype=float)
        self.difficulty = difficulty
        self.detail_level = detail_level
        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level)
    
    @staticmethod
    def _generate_matrix(size: int, max_coef: int) -> List[List[float]]:
        """Генерирует систему с единственным решением."""
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Генерируем решение
            x = [random.randint(-max_coef, max_coef) for _ in range(size)]
            
            # Генерируем коэффициенты A
            A = [[random.randint(-max_coef, max_coef) for _ in range(size)] for _ in range(size)]
            
            # Проверяем определитель
            A_np = np.array(A, dtype=float)
            det = np.linalg.det(A_np)
            
            if abs(det) > 0.1:  # Система имеет единственное решение
                # Вычисляем правую часть b = A * x
                matrix = []
                for i in range(size):
                    b_i = sum(A[i][j] * x[j] for j in range(size))
                    row = A[i] + [b_i]
                    matrix.append(row)
                return matrix
        
        # Fallback: простая система
        return [[1, 0, 1], [0, 1, 2]] if size == 2 else [[1, 0, 0, 1], [0, 1, 0, 2], [0, 0, 1, 3]]

    def _create_problem_description(self, language: str):
        n = self.matrix.shape[0]
        variables = [f"x{i+1}" for i in range(n)]
        equations = []
        for row in self.matrix:
            terms = []
            for i in range(n):
                coeff = row[i]
                var = variables[i]
                sign = "" if i == 0 else (" + " if coeff >= 0 else " - ")
                coeff_abs = abs(coeff)
                term = f"{'' if coeff_abs==1 else coeff_abs}{var}"
                terms.append(sign + term)
            eq = "".join(terms) + f" = {row[-1]}"
            equations.append(eq)
        joined = "\n".join(equations)
        if language.lower() == "ru":
            return PROMPT_TEMPLATES["system_linear"]["problem"]["ru"].format(equations=joined)
        else:
            return PROMPT_TEMPLATES["system_linear"]["problem"]["en"].format(equations=joined)

    def solve(self):
        matrix = self.matrix
        A = matrix[:, :-1]
        B = matrix[:, -1]
        n = A.shape[0]
        if A.shape[0] != A.shape[1]:
            error_str = PROMPT_TEMPLATES["default"]["error"]["en"].format(error="Матрица коэффициентов должна быть квадратной")
            raise ValueError(error_str)
        steps = []
        det_A = np.linalg.det(A)
        if self.detail_level >= 2:
            if self.language == "ru":
                steps.append(f"Шаг 1: Вычисляем главный определитель системы: det(A) = {det_A:.2f}")
            else:
                steps.append(f"Step 1: Compute det(A) = {det_A:.2f}")
        if abs(det_A) < 1e-6:
            no_unique = PROMPT_TEMPLATES["system_linear"]["no_unique_solution"].get(self.language, PROMPT_TEMPLATES["system_linear"]["no_unique_solution"]["en"])
            steps.append(no_unique)
            self.solution_steps.extend(steps)
            self.final_answer = no_unique
            return
        X = []
        for i in range(n):
            A_i = A.copy()
            A_i[:, i] = B
            det_Ai = np.linalg.det(A_i)
            x_i = det_Ai / det_A
            X.append(x_i)
            if self.detail_level >= 3:
                step_num = i*2 + 2
                message1 = PROMPT_TEMPLATES["system_linear"]["step"].get(self.language, PROMPT_TEMPLATES["system_linear"]["step"]["en"]).format(step_num=step_num, message=f"Заменяем {i+1}-й столбец и вычисляем det(A_{i+1}) = {det_Ai:.2f}")
                message2 = PROMPT_TEMPLATES["system_linear"]["step"].get(self.language, PROMPT_TEMPLATES["system_linear"]["step"]["en"]).format(step_num=step_num+1, message=f"x{i+1} = det(A_{i+1}) / det(A) = {x_i:.2f}")
                steps.extend([message1, message2])
        self.solution_steps.extend(steps)
        self.final_answer = ", ".join([f"x{i+1} = {x:.2f}" for i, x in enumerate(X)])

    def get_task_type(self):
        return "system_linear"
