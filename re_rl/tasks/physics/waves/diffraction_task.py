# re_rl/tasks/physics/waves/diffraction_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DiffractionTask(BaseMathTask):
    """Задачи на дифракцию света."""
    
    TASK_TYPES = ["single_slit", "grating", "resolving_power"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.a = round(random.uniform(1, 50), 1)  # мкм (ширина щели)
        self.wavelength = round(random.uniform(400, 700), 0)  # нм
        self.N_lines = random.randint(100, 1000)  # штрихов/мм
        self.N_total = random.randint(1000, 10000)  # общее число штрихов
        self.m = random.randint(1, 3)  # порядок
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["diffraction"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "single_slit":
            text += t["problem"]["single_slit"][self.language].format(
                a=self.a, **{"lambda": self.wavelength})
        elif self.task_type == "grating":
            text += t["problem"]["grating"][self.language].format(
                N=self.N_lines, m=self.m, **{"lambda": self.wavelength})
        else:
            text += t["problem"]["resolving_power"][self.language].format(
                N=self.N_total, m=self.m)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["diffraction"]
        steps = []
        
        if self.task_type == "single_slit":
            steps.append(t["steps"]["slit_minimum"][self.language])
            a_m = self.a * 1e-6
            lambda_m = self.wavelength * 1e-9
            sin_theta = lambda_m / a_m  # первый минимум, m=1
            if sin_theta <= 1:
                theta = math.degrees(math.asin(sin_theta))
                steps.append(f"sin(θ) = λ/a = {self.wavelength}·10⁻⁹/{self.a}·10⁻⁶ = {round(sin_theta, 6)}")
                steps.append(f"θ = arcsin({round(sin_theta, 6)}) = {round(theta, 3)}°")
                answer = f"θ = {round(theta, 3)}°"
            else:
                answer = "Минимум не наблюдается (sin(θ) > 1)"
        elif self.task_type == "grating":
            steps.append(t["steps"]["grating_maximum"][self.language])
            d = 1 / self.N_lines * 1e-3  # период в м
            lambda_m = self.wavelength * 1e-9
            sin_theta = self.m * lambda_m / d
            if sin_theta <= 1:
                theta = math.degrees(math.asin(sin_theta))
                steps.append(f"d = 1/{self.N_lines} мм = {d*1e6:.2f} мкм")
                steps.append(f"sin(θ) = {self.m}·{self.wavelength}·10⁻⁹/{d:.2e} = {round(sin_theta, 6)}")
                steps.append(f"θ = {round(theta, 2)}°")
                answer = f"θ = {round(theta, 2)}°"
            else:
                answer = f"Максимум {self.m}-го порядка не наблюдается"
        else:
            steps.append(t["steps"]["resolving"][self.language])
            R = self.m * self.N_total
            steps.append(f"R = m·N = {self.m}·{self.N_total} = {R}")
            answer = f"R = {R}"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "diffraction"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
