class BaseTask:
    """
    Базовый класс для текстовых задач.
    Определяет общий интерфейс для постановки задачи, генерации промта и получения решения.
    """
    def __init__(self, description: str):
        self.description = description
        self.solution_steps = []
        self.final_answer = None

    def generate_prompt(self) -> str:
        return f"Задача: {self.description}\n Пожалуйста, решите задачу пошагово."

    def solve(self):
        raise NotImplementedError("Метод solve должен быть реализован в подклассах.")

    def get_result(self) -> dict:
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
