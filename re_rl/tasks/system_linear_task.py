# re_rl/tasks/system_linear_task.py

import numpy as np
from re_rl.tasks.base_task import BaseMathTask

class SystemLinearTask(BaseMathTask):
    """
    Класс для решения системы линейных уравнений методом Крамера.
    Коэффициенты задаются как список уравнений: [[a11, a12, ..., b1], ...].
    """
    def __init__(self, matrix, language: str = "ru"):
        self.matrix = np.array(matrix, dtype=float)
        description = self._create_problem_description()
        super().__init__(description, language)

    def _create_problem_description(self):
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
        return "Решите систему уравнений:\n" + "\n".join(equations)

    def solve(self):
        matrix = self.matrix
        A = matrix[:, :-1]
        B = matrix[:, -1]
        n = A.shape[0]
        if A.shape[0] != A.shape[1]:
            raise ValueError("Матрица коэффициентов должна быть квадратной")
        det_A = np.linalg.det(A)
        self.solution_steps.append(f"Шаг 1: Вычисляем главный определитель системы: det(A) = {det_A:.2f}")
        if abs(det_A) < 1e-6:
            self.solution_steps.append("Система либо несовместна, либо имеет бесконечно много решений")
            self.final_answer = "Нет единственного решения"
            return
        X = []
        for i in range(n):
            A_i = A.copy()
            A_i[:, i] = B
            det_Ai = np.linalg.det(A_i)
            x_i = det_Ai / det_A
            X.append(x_i)
            self.solution_steps.append(f"Шаг {i+2}: Заменяем {i+1}-й столбец и находим det(A_{i+1}) = {det_Ai:.2f}")
            self.solution_steps.append(f"x{i+1} = det(A_{i+1}) / det(A) = {x_i:.2f}")
        self.final_answer = ", ".join([f"x{i+1} = {x:.2f}" for i, x in enumerate(X)])

    def get_task_type(self):
        return "math"
