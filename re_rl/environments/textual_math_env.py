# re_rl/environments/textual_math_env.py
"""
Интерфейс для выдачи задач в процессе тренировки LLM.
"""

import random
from re_rl.tasks import (
    # Математика
    ArithmeticTask,
    LinearTask,
    QuadraticTask,
    NumberTheoryTask,
    StatisticsTask,
    # Физика
    KinematicsTask,
    CircuitsTask,
    GasLawsTask,
)


class TextualMathEnv:
    """
    Интерфейс для выдачи задач в процессе тренировки LLM.
    
    Параметры:
        task_types: список типов задач для генерации
        language: язык задач ("ru" или "en")
        difficulty: уровень сложности (1-10)
        include_physics: включать ли физические задачи
    """
    
    MATH_TASKS = {
        "arithmetic": ArithmeticTask,
        "linear": LinearTask,
        "quadratic": QuadraticTask,
        "number_theory": NumberTheoryTask,
        "statistics": StatisticsTask,
    }
    
    PHYSICS_TASKS = {
        "kinematics": KinematicsTask,
        "circuits": CircuitsTask,
        "gas_laws": GasLawsTask,
    }
    
    def __init__(
        self, 
        task_types=None, 
        language: str = "ru",
        difficulty: int = 5,
        include_physics: bool = False
    ):
        self.language = language
        self.difficulty = difficulty
        
        # Объединяем все задачи
        self._task_classes = {**self.MATH_TASKS}
        if include_physics:
            self._task_classes.update(self.PHYSICS_TASKS)
        
        # Типы задач
        if task_types:
            self.task_types = [t for t in task_types if t in self._task_classes]
        else:
            self.task_types = list(self._task_classes.keys())

    def get_task(self):
        """Возвращает случайную задачу."""
        task_type = random.choice(self.task_types)
        task_class = self._task_classes.get(task_type, ArithmeticTask)
        
        task = task_class(
            difficulty=self.difficulty,
            language=self.language
        )
        
        # Для новых задач (BaseMathTask) используем solve()
        if hasattr(task, 'solve') and not hasattr(task, 'get_result'):
            task.solve()
            return {
                "problem": task.description,
                "prompt": task.description,
                "solution_steps": task.solution_steps,
                "final_answer": task.final_answer,
                "task_type": task_type,
            }
        
        # Для старых задач
        result = task.get_result()
        result["task_type"] = task_type
        return result
    
    def get_task_with_difficulty(self, difficulty: int):
        """Возвращает задачу с указанным уровнем сложности."""
        old_difficulty = self.difficulty
        self.difficulty = difficulty
        result = self.get_task()
        self.difficulty = old_difficulty
        return result
    
    def get_physics_task(self):
        """Возвращает случайную физическую задачу."""
        task_type = random.choice(list(self.PHYSICS_TASKS.keys()))
        task_class = self.PHYSICS_TASKS[task_type]
        
        task = task_class(
            difficulty=self.difficulty,
            language=self.language
        )
        task.solve()
        
        return {
            "problem": task.description,
            "prompt": task.description,
            "solution_steps": task.solution_steps,
            "final_answer": task.final_answer,
            "task_type": task_type,
        }


# Пример использования интерфейса
if __name__ == "__main__":
    print("=" * 60)
    print("Пример: Математическая задача")
    print("=" * 60)
    
    env = TextualMathEnv(language="ru", difficulty=5)
    result = env.get_task()
    print(f"Тип: {result['task_type']}")
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
    
    print("\n" + "=" * 60)
    print("Пример: Физическая задача")
    print("=" * 60)
    
    env = TextualMathEnv(language="ru", difficulty=5, include_physics=True)
    result = env.get_physics_task()
    print(f"Тип: {result['task_type']}")
    print(f"Задача: {result['problem']}")
    print(f"Ответ: {result['final_answer']}")
