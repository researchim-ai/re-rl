# re_rl/tasks/system_linear_task.py

import numpy as np
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class SystemLinearTask(BaseMathTask):
    """
    Решает систему линейных уравнений методом Крамера.
    Коэффициенты задаются как список уравнений: [[a11, a12, ..., b1], ...].
    detail_level определяет количество шагов решения.
    """
    def __init__(self, matrix, language: str = "ru", detail_level: int = 3):
        self.matrix = np.array(matrix, dtype=float)
        self.detail_level = detail_level
        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level)

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
