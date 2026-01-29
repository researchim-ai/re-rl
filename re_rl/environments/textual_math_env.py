# re_rl/environments/textual_math_env.py
"""
Интерфейс для выдачи задач в процессе тренировки LLM.
"""

import random
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.arithmetic_task import ArithmeticTask


class TextualMathEnv:
    """
    Интерфейс для выдачи задач в процессе тренировки LLM.
    
    Параметры:
        task_types: список типов задач для генерации
        language: язык задач ("ru" или "en")
        difficulty: уровень сложности (1-10)
    """
    
    def __init__(
        self, 
        task_types=None, 
        language: str = "ru",
        difficulty: int = 5
    ):
        self.task_types = task_types or ["arithmetic", "linear", "quadratic"]
        self.language = language
        self.difficulty = difficulty
        
        self._task_classes = {
            "arithmetic": ArithmeticTask,
            "linear": LinearTask,
            "quadratic": QuadraticTask,
        }

    def get_task(self):
        """Возвращает случайную задачу."""
        task_type = random.choice(self.task_types)
        task_class = self._task_classes.get(task_type, ArithmeticTask)
        
        task = task_class(
            difficulty=self.difficulty,
            language=self.language
        )
        
        return task.get_result()
    
    def get_task_with_difficulty(self, difficulty: int):
        """Возвращает задачу с указанным уровнем сложности."""
        task_type = random.choice(self.task_types)
        task_class = self._task_classes.get(task_type, ArithmeticTask)
        
        task = task_class(
            difficulty=difficulty,
            language=self.language
        )
        
        return task.get_result()


# Пример использования интерфейса
if __name__ == "__main__":
    env = TextualMathEnv()
    result = env.get_task()
    print("Постановка задачи:")
    print(result["problem"])
    print("\nПромт:")
    print(result["prompt"])
    print("\nПошаговое решение:")
    for step in result["solution_steps"]:
        print(step)
    print("\nИтоговый ответ:")
    print(result["final_answer"])
