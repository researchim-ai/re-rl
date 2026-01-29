# re_rl/tasks/physics/waves/polarization_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class PolarizationTask(BaseMathTask):
    """Задачи на поляризацию света."""
    
    TASK_TYPES = ["malus", "brewster", "two_polarizers"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.I0 = round(random.uniform(10, 1000), 1)  # Вт/м²
        self.angle = round(random.uniform(10, 80), 1)  # градусы
        self.n = round(random.uniform(1.3, 1.8), 2)  # показатель преломления
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["polarization"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "malus":
            text += t["problem"]["malus"][self.language].format(I0=self.I0, angle=self.angle)
        elif self.task_type == "brewster":
            text += t["problem"]["brewster"][self.language].format(n=self.n)
        else:
            text += t["problem"]["two_polarizers"][self.language].format(I0=self.I0, angle=self.angle)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["polarization"]
        steps = []
        
        if self.task_type == "malus":
            steps.append(t["steps"]["malus_law"][self.language])
            angle_rad = math.radians(self.angle)
            I = self.I0 * math.cos(angle_rad) ** 2
            steps.append(f"I = {self.I0}·cos²({self.angle}°) = {self.I0}·{round(math.cos(angle_rad)**2, 4)} = {round(I, 2)} Вт/м²")
            answer = f"I = {round(I, 2)} Вт/м²"
        elif self.task_type == "brewster":
            steps.append(t["steps"]["brewster_formula"][self.language])
            theta_B = math.degrees(math.atan(self.n))
            steps.append(f"tan(θ_B) = n = {self.n}")
            steps.append(f"θ_B = arctg({self.n}) = {round(theta_B, 2)}°")
            answer = f"θ_B = {round(theta_B, 2)}°"
        else:
            steps.append(t["steps"]["unpolarized"][self.language])
            steps.append(t["steps"]["malus_law"][self.language])
            I1 = self.I0 / 2
            angle_rad = math.radians(self.angle)
            I2 = I1 * math.cos(angle_rad) ** 2
            steps.append(f"I₁ = {self.I0}/2 = {round(I1, 2)} Вт/м²")
            steps.append(f"I₂ = {round(I1, 2)}·cos²({self.angle}°) = {round(I2, 2)} Вт/м²")
            answer = f"I = {round(I2, 2)} Вт/м²"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "polarization"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
