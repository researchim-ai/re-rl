# re_rl/tasks/base_task.py

from re_rl.tasks.prompts import PROMPT_TEMPLATES

class BaseTask:
    """
    Базовый класс для текстовых задач.
    """
    def __init__(self, description: str):
        self.description = description
        self.solution_steps = []
        self.final_answer = None

    def generate_prompt(self) -> str:
        default = PROMPT_TEMPLATES["default"]["prompt"]
        lang = getattr(self, "language", "en").lower()
        prompt_template = default.get(lang, default["en"])
        return prompt_template.format(problem=self.description)

    def solve(self):
        raise NotImplementedError("Метод solve() должен быть реализован в подклассах.")

    def get_result(self) -> dict:
        """
        Возвращает полный результат решения задачи, включая шаги, объяснения и валидации.
        """
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        
        result = {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
        
        if self.explanation_steps:
            result["explanations"] = self.explanation_steps
        if self.validation_steps:
            result["validations"] = self.validation_steps
            
        return result

class BaseMathTask(BaseTask):
    """
    Базовый класс для математических задач с поддержкой многоязычности и настраиваемой детализацией.
    """
    def __init__(self, description: str, language: str = "ru", detail_level: int = 3):
        super().__init__(description)
        self.language = language.lower()
        self.detail_level = detail_level
        self.solution_steps = []
        self.validation_steps = []
        self.explanation_steps = []
        self.final_answer = None

    def generate_prompt(self) -> str:
        default = PROMPT_TEMPLATES["default"]["prompt"]
        prompt_template = default.get(self.language, default["en"])
        return prompt_template.format(problem=self.description)

    def add_solution_step(self, step: str, explanation: str = None, validation: str = None):
        """
        Добавляет шаг решения с опциональным объяснением и валидацией.
        """
        self.solution_steps.append(step)
        if explanation:
            self.explanation_steps.append(explanation)
        if validation:
            self.validation_steps.append(validation)

    def validate_step(self, step_index: int) -> bool:
        """
        Проверяет корректность шага решения.
        """
        if 0 <= step_index < len(self.solution_steps):
            return True
        return False

    def get_step_explanation(self, step_index: int) -> str:
        """
        Возвращает объяснение для конкретного шага.
        """
        if 0 <= step_index < len(self.explanation_steps):
            return self.explanation_steps[step_index]
        return ""

    def get_step_validation(self, step_index: int) -> str:
        """
        Возвращает валидацию для конкретного шага.
        """
        if 0 <= step_index < len(self.validation_steps):
            return self.validation_steps[step_index]
        return ""

    def generate_latex_solution(self) -> str:
        import sympy as sp
        latex_steps = []
        for i, step in enumerate(self.solution_steps):
            try:
                expr = sp.sympify(step)
                latex_steps.append(sp.latex(expr))
                if self.get_step_explanation(i):
                    latex_steps.append(r"\text{" + self.get_step_explanation(i) + "}")
                if self.get_step_validation(i):
                    latex_steps.append(r"\text{" + self.get_step_validation(i) + "}")
            except Exception:
                safe_step = step.replace("_", r"\_").replace("%", r"\%")
                latex_steps.append(r"\text{" + safe_step + "}")
        return r"\begin{align*}" + " \\\\\n".join(latex_steps) + r"\end{align*}"

    def get_task_type(self):
        raise NotImplementedError("Метод get_task_type() должен быть реализован в подклассах.")

    def get_result(self) -> dict:
        """
        Возвращает полный результат решения задачи, включая шаги, объяснения и валидации.
        """
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        
        result = {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
        
        if self.explanation_steps:
            result["explanations"] = self.explanation_steps
        if self.validation_steps:
            result["validations"] = self.validation_steps
            
        return result
