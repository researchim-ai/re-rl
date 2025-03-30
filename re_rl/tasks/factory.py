# re_rl/tasks/factory.py

import random
import numpy as np

from re_rl.tasks.linear_task import LinearTask
from re_rl.tasks.quadratic_task import QuadraticTask
from re_rl.tasks.cubic_task import CubicTask
from re_rl.tasks.exponential_task import ExponentialTask
from re_rl.tasks.logarithmic_task import LogarithmicTask
from re_rl.tasks.calculus_task import CalculusTask
from re_rl.tasks.analogical_task import AnalogicalTask
from re_rl.tasks.knights_knaves_task import KnightsKnavesTask
from re_rl.tasks.contradiction_task import ContradictionTask
from re_rl.tasks.graph_task import GraphTask
from re_rl.tasks.futoshiki_task import FutoshikiTask
from re_rl.tasks.urn_probability_task import UrnProbabilityTask
from re_rl.tasks.text_stats_task import TextStatsTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class MathTaskFactory:
    @classmethod
    def generate_random_math_task(cls, only_valid: bool = False, language: str = "ru", detail_level: int = 3):
        types = ["linear", "quadratic", "cubic", "exponential", "logarithmic"]
        eq_type = random.choice(types)

        if eq_type == "linear":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            task = LinearTask(a, b, c, language, detail_level)

        elif eq_type == "quadratic":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            task = QuadraticTask(a, b, c, language, detail_level)

        elif eq_type == "cubic":
            a = random.choice([i for i in range(-10, 11) if i != 0])
            b = random.randint(-10, 10)
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = CubicTask(a, b, c, d, language, detail_level)

        elif eq_type == "exponential":
            a = random.choice([i for i in range(-5, 6) if i != 0])
            b = random.choice([i for i in range(-5, 6) if i != 0])
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = ExponentialTask(a, b, c, d, language, detail_level)

        elif eq_type == "logarithmic":
            a = random.choice([i for i in range(-5, 6) if i != 0])
            b = random.choice([i for i in range(1, 11)])
            c = random.randint(-10, 10)
            d = random.randint(-10, 10)
            task = LogarithmicTask(a, b, c, d, language, detail_level)

        else:
            raise ValueError("Неподдерживаемый тип уравнения.")

        if not only_valid:
            return task

        no_solution_str = PROMPT_TEMPLATES["default"]["no_solution"].get(language, PROMPT_TEMPLATES["default"]["no_solution"]["en"])
        result = task.get_result()
        if result["final_answer"] != no_solution_str:
            return task
        else:
            return cls.generate_random_math_task(only_valid=only_valid, language=language, detail_level=detail_level)

    @classmethod
    def generate_random_task(cls, only_valid: bool = False, language: str = "ru", detail_level: int = 3):
        categories = [
            "math",
            "graph",
            "calculus",
            "analogical",
            "contradiction",
            "knights_knaves",
            "futoshiki",
            "urn_probability",
            "text_stats"
        ]
        task_category = random.choice(categories)

        if task_category == "math":
            return cls.generate_random_math_task(only_valid=only_valid, language=language, detail_level=detail_level)

        elif task_category == "graph":
            task = GraphTask.generate_random_task(only_valid=only_valid, language=language, detail_level=detail_level)

        elif task_category == "calculus":
            task_type = random.choice(["differentiation", "integration"])
            task = CalculusTask.generate_random_task(task_type=task_type, language=language, detail_level=detail_level)

        elif task_category == "analogical":
            descriptions = [
                "In biology, scientists use the structure of the human eye to understand how cameras work. How might this analogy be used to solve a problem with a malfunctioning camera?",
                "City planners often use the analogy of a living organism to understand urban development. How might this analogy be used to address traffic congestion in a growing city?"
            ]
            desc = random.choice(descriptions)
            task = AnalogicalTask(desc, language=language, detail_level=detail_level)

        elif task_category == "contradiction":
            # Число утверждений можно выбрать случайно
            num_statements = random.randint(5, 12)
            task = ContradictionTask(language=language, num_statements=num_statements)

        elif task_category == "knights_knaves":
            task = KnightsKnavesTask(language=language, detail_level=detail_level)

        elif task_category == "futoshiki":
            task = FutoshikiTask(language=language, detail_level=detail_level)

        elif task_category == "urn_probability":
            task = UrnProbabilityTask(language=language)
        elif task_category == "text_stats":
            # Дополнительно, при желании, можно рандомить allow_overlapping
            # или заданный текст, чтобы повысить вариативность
            task = TextStatsTask(
                language=language, 
                detail_level=detail_level, 
                allow_overlapping=bool(random.getrandbits(1))
            )
        else:
            raise ValueError("Unsupported task category.")

        if not only_valid:
            return task

        no_solution_str = PROMPT_TEMPLATES["default"]["no_solution"].get(language, PROMPT_TEMPLATES["default"]["no_solution"]["en"])
        result = task.get_result()
        if result["final_answer"] != no_solution_str:
            return task
        else:
            return cls.generate_random_task(only_valid=only_valid, language=language, detail_level=detail_level)
