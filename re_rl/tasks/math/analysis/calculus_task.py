# re_rl/tasks/calculus_task.py

import random
import sympy as sp
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any, ClassVar

class CalculusTask(BaseMathTask):
    """
    Задачи по анализу: дифференцирование или интегрирование полиномиальных функций.
    task_type: "differentiation" или "integration".
    detail_level контролирует степень детализации.
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"degree": 1},
        3: {"degree": 2},
        5: {"degree": 3},
        7: {"degree": 4},
        10: {"degree": 5},
    }
    
    def __init__(
        self, 
        task_type="differentiation", 
        degree=2, 
        function=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            degree = preset.get("degree", degree)
        
        self.task_type = task_type.lower()
        self.degree = degree
        self.function = function
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        super().__init__("", language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def generate_function(self):
        if self.function is None:
            x = sp.symbols('x')
            coeffs = [random.randint(-5, 5) for _ in range(self.degree+1)]
            while coeffs[-1] == 0:
                coeffs[-1] = random.randint(-5, 5)
            poly = sum(coeffs[i]*x**i for i in range(self.degree+1))
            self.function = sp.simplify(poly)

    def _create_problem_description(self):
        self.generate_function()
        is_latex = self._output_format == "latex"
        templates = PROMPT_TEMPLATES["calculus"]
        
        # Форматируем функцию
        if is_latex:
            func_latex = sp.latex(self.function)
            if self.task_type == "differentiation":
                expression = f"$\\frac{{d}}{{dx}}\\left({func_latex}\\right)$"
                return templates["problem_derivative"][self.language].format(expression=expression)
            else:
                expression = f"$\\int {func_latex} \\, dx$"
                return templates["problem_integral"][self.language].format(expression=expression)
        else:
            func_str = sp.pretty(self.function)
            task_type_text = templates["task_type_derivative" if self.task_type == "differentiation" else "task_type_integral"][self.language]
            return templates["problem"][self.language].format(task_type=task_type_text, function_pretty=func_str)

    def solve(self):
        x = sp.symbols('x')
        self.description = self._create_problem_description()
        is_latex = self._output_format == "latex"
        step_tmpl = PROMPT_TEMPLATES["default"]["step"][self.language]
        func_label = PROMPT_TEMPLATES["default"]["function"][self.language]
        
        steps = []
        
        # Шаг 1
        if is_latex:
            func_latex = sp.latex(self.function)
            text = f"{func_label}: $f(x) = {func_latex}$"
        else:
            text = f"{func_label}: f(x) = {sp.pretty(self.function)}"
        steps.append(step_tmpl.format(n=1, text=text))
        
        if self.task_type == "differentiation":
            result_expr = sp.diff(self.function, x)
            
            if is_latex:
                result_latex = sp.latex(result_expr)
                text = f"$f'(x) = {result_latex}$"
                self.final_answer = f"$f'(x) = {result_latex}$"
            else:
                text = f"f'(x) = {sp.pretty(result_expr)}"
                self.final_answer = sp.pretty(result_expr)
            steps.append(step_tmpl.format(n=2, text=text))
                
        elif self.task_type == "integration":
            result_expr = sp.integrate(self.function, x)
            
            if is_latex:
                result_latex = sp.latex(result_expr)
                text = f"$\\int f(x) \\, dx = {result_latex} + C$"
                self.final_answer = f"${result_latex} + C$"
            else:
                text = f"∫f(x)dx = {sp.pretty(result_expr)} + C"
                self.final_answer = sp.pretty(result_expr) + " + C"
            steps.append(step_tmpl.format(n=2, text=text))
        else:
            error_msg = PROMPT_TEMPLATES["default"]["no_solution"].get(self.language, "No solution")
            steps.append(error_msg)
            self.final_answer = error_msg
        
        self.solution_steps.extend(steps)

    def get_task_type(self):
        return "calculus"

    @classmethod
    def generate_random_task(
        cls, 
        task_type="differentiation", 
        degree=None, 
        language: str = "ru", 
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text"
    ):
        if degree is None:
            degree = random.randint(1, 3)
        task = cls(
            task_type=task_type, 
            degree=degree, 
            language=language, 
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format
        )
        task.solve()
        return task

    def get_result(self, detail_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Возвращает результат решения с заданным уровнем детализации.
        
        Args:
            detail_level: Уровень детализации решения. Если не указан, используется self.detail_level
            
        Returns:
            Dict[str, Any]: Результат решения
        """
        if detail_level is None:
            detail_level = self.detail_level
            
        result = super().get_result()
        
        # Решаем задачу, если еще не решена
        if not self.solution_steps:
            self.solve()
            
        result["final_answer"] = self.final_answer
        return result
