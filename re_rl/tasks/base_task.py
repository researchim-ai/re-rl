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
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }

class BaseMathTask(BaseTask):
    """
    Базовый класс для математических задач с поддержкой многоязычности и настраиваемой детализацией.
    """
    def __init__(self, description: str, language: str = "ru", detail_level: int = 3):
        super().__init__(description)
        self.language = language.lower()
        self.detail_level = detail_level

    def generate_prompt(self) -> str:
        default = PROMPT_TEMPLATES["default"]["prompt"]
        prompt_template = default.get(self.language, default["en"])
        return prompt_template.format(problem=self.description)

    def generate_latex_solution(self) -> str:
        import sympy as sp
        latex_steps = []
        for step in self.solution_steps:
            try:
                expr = sp.sympify(step)
                latex_steps.append(sp.latex(expr))
            except Exception:
                safe_step = step.replace("_", r"\_").replace("%", r"\%")
                latex_steps.append(r"\text{" + safe_step + "}")
        return r"\begin{align*}" + " \\\\\n".join(latex_steps) + r"\end{align*}"

    def get_task_type(self):
        raise NotImplementedError("Метод get_task_type() должен быть реализован в подклассах.")
