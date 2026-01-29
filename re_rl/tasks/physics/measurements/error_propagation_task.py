# re_rl/tasks/physics/measurements/error_propagation_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ErrorPropagationTask(BaseMathTask):
    """Задачи на распространение погрешностей."""
    
    TASK_TYPES = ["sum_difference", "product", "power", "formula"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Генерируем измерения с погрешностями
        self.A = round(random.uniform(10, 100), 1)
        self.dA = round(self.A * random.uniform(0.01, 0.1), 2)
        self.B = round(random.uniform(5, 50), 1)
        self.dB = round(self.B * random.uniform(0.01, 0.1), 2)
        self.x = round(random.uniform(2, 20), 2)
        self.dx = round(self.x * random.uniform(0.01, 0.05), 3)
        self.n = random.randint(2, 4)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["error_propagation"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "sum_difference":
            text += t["problem"]["sum_difference"][self.language].format(
                A=self.A, dA=self.dA, B=self.B, dB=self.dB)
        elif self.task_type == "product":
            text += t["problem"]["product"][self.language].format(
                A=self.A, dA=self.dA, B=self.B, dB=self.dB)
        elif self.task_type == "power":
            text += t["problem"]["power"][self.language].format(
                x=self.x, dx=self.dx, n=self.n)
        else:
            text += t["problem"]["formula"][self.language].format(
                formula="S = πr²",
                variables=f"r = {self.x} ± {self.dx} м")
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["error_propagation"]
        steps = []
        
        if self.task_type == "sum_difference":
            steps.append(t["steps"]["sum_rule"][self.language])
            result = self.A + self.B
            d_result = math.sqrt(self.dA**2 + self.dB**2)
            steps.append(f"A + B = {self.A} + {self.B} = {round(result, 1)}")
            steps.append(f"Δ(A+B) = √({self.dA}² + {self.dB}²) = {round(d_result, 3)}")
            answer = f"({round(result, 1)} ± {round(d_result, 3)})"
        elif self.task_type == "product":
            steps.append(t["steps"]["product_rule"][self.language])
            result = self.A * self.B
            rel_A = self.dA / self.A
            rel_B = self.dB / self.B
            rel_result = math.sqrt(rel_A**2 + rel_B**2)
            d_result = result * rel_result
            steps.append(f"A·B = {self.A}·{self.B} = {round(result, 2)}")
            steps.append(f"δA = {self.dA}/{self.A} = {round(rel_A, 4)}")
            steps.append(f"δB = {self.dB}/{self.B} = {round(rel_B, 4)}")
            steps.append(f"δ(A·B) = √({round(rel_A, 4)}² + {round(rel_B, 4)}²) = {round(rel_result, 4)}")
            steps.append(f"Δ(A·B) = {round(result, 2)}·{round(rel_result, 4)} = {round(d_result, 2)}")
            answer = f"({round(result, 2)} ± {round(d_result, 2)})"
        elif self.task_type == "power":
            steps.append(t["steps"]["power_rule"][self.language])
            result = self.x ** self.n
            rel_x = self.dx / self.x
            rel_result = self.n * rel_x
            d_result = result * rel_result
            steps.append(f"x^{self.n} = {self.x}^{self.n} = {round(result, 3)}")
            steps.append(f"δx = {self.dx}/{self.x} = {round(rel_x, 4)}")
            steps.append(f"δ(x^{self.n}) = {self.n}·{round(rel_x, 4)} = {round(rel_result, 4)}")
            steps.append(f"Δ(x^{self.n}) = {round(result, 3)}·{round(rel_result, 4)} = {round(d_result, 3)}")
            answer = f"({round(result, 3)} ± {round(d_result, 3)})"
        else:
            # Площадь круга
            steps.append("S = πr², δS = 2·δr")
            S = math.pi * self.x ** 2
            rel_r = self.dx / self.x
            rel_S = 2 * rel_r
            dS = S * rel_S
            steps.append(f"S = π·{self.x}² = {round(S, 3)} м²")
            steps.append(f"δr = {self.dx}/{self.x} = {round(rel_r, 4)}")
            steps.append(f"δS = 2·{round(rel_r, 4)} = {round(rel_S, 4)}")
            steps.append(f"ΔS = {round(S, 3)}·{round(rel_S, 4)} = {round(dS, 3)} м²")
            answer = f"S = ({round(S, 3)} ± {round(dS, 3)}) м²"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "error_propagation"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
