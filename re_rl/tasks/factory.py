# re_rl/tasks/factory.py

import random
from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.system_linear_task import SystemLinearTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.graph_task import GraphTask

class MathTaskFactory:
    @classmethod
    def generate_random_math_task(cls, only_valid: bool = False, language: str = "ru"):
        types = ["linear", "quadratic", "cubic", "exponential", "logarithmic"]
        eq_type = random.choice(types)
        if eq_type == "linear":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            task = LinearTask(a, b, c, language)
        elif eq_type == "quadratic":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            task = QuadraticTask(a, b, c, language)
        elif eq_type == "cubic":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = CubicTask(a, b, c, d, language)
        elif eq_type == "exponential":
            a = random.choice([i for i in range(-5, 6) if i != 0])
            b = random.choice([i for i in range(-5, 6) if i != 0])
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = ExponentialTask(a, b, c, d, language)
        elif eq_type == "logarithmic":
            a = random.choice([i for i in range(-5, 6) if i != 0])
            b = random.choice([i for i in range(1, 11)])
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = LogarithmicTask(a, b, c, d, language)
        else:
            raise ValueError("Неподдерживаемый тип уравнения.")
        if not only_valid:
            return task
        result = task.get_result()
        if result["final_answer"] != "Нет решений":
            return task
        else:
            return cls.generate_random_math_task(only_valid=only_valid, language=language)

    @classmethod
    def generate_random_task(cls, only_valid: bool = False, language: str = "ru"):
        task_category = random.choice(["math", "graph", "calculus"])
        if task_category == "math":
            return cls.generate_random_math_task(only_valid=only_valid, language=language)
        elif task_category == "graph":
            return GraphTask.generate_random_task(only_valid=only_valid, language=language)
        elif task_category == "calculus":
            task_type = random.choice(["differentiation", "integration"])
            return CalculusTask.generate_random_task(task_type=task_type, language=language)
        else:
            raise ValueError("Неподдерживаемая категория задачи.")
