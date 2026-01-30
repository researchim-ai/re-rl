# re_rl/tasks/physics/waves/interference_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class InterferenceTask(BaseMathTask):
    """Задачи на интерференцию света."""
    
    TASK_TYPES = ["double_slit", "thin_film", "max_order"]

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode=False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.d = round(random.uniform(0.1, 1.0), 2)  # мм
        self.L = round(random.uniform(0.5, 3.0), 1)  # м
        self.wavelength = round(random.uniform(400, 700), 0)  # нм
        self.t = round(random.uniform(100, 500), 0)  # нм (толщина плёнки)
        self.n = round(random.uniform(1.3, 1.6), 2)  # показатель преломления
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["interference"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "double_slit":
            text += t["problem"]["double_slit"][self.language].format(
                d=self.d, L=self.L, **{"lambda": self.wavelength})
        elif self.task_type == "thin_film":
            text += t["problem"]["thin_film"][self.language].format(
                t=self.t, n=self.n, **{"lambda": self.wavelength})
        else:
            text += t["problem"]["max_order"][self.language].format(
                d=self.d * 1000, **{"lambda": self.wavelength})  # мкм
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["interference"]
        steps = []
        
        if self.task_type == "double_slit":
            steps.append(t["steps"]["fringe_spacing"][self.language])
            # Δx = λL/d
            d_m = self.d * 1e-3  # мм -> м
            lambda_m = self.wavelength * 1e-9  # нм -> м
            delta_x = lambda_m * self.L / d_m
            steps.append(f"Δx = {self.wavelength}·10⁻⁹·{self.L}/({self.d}·10⁻³) = {round(delta_x*1000, 4)} мм")
            answer = f"Δx = {round(delta_x*1000, 4)} мм"
        elif self.task_type == "thin_film":
            steps.append(t["steps"]["path_difference"][self.language])
            delta = 2 * self.n * self.t
            steps.append(f"δ = 2·{self.n}·{self.t} = {round(delta, 1)} нм")
            answer = f"δ = {round(delta, 1)} нм"
        else:
            steps.append(t["steps"]["max_condition"][self.language])
            d_um = self.d * 1000  # мм -> мкм
            lambda_um = self.wavelength / 1000  # нм -> мкм
            m_max = int(d_um / lambda_um)
            steps.append(f"m_max = d/λ = {d_um}/{lambda_um:.3f} ≈ {m_max}")
            answer = f"m_max = {m_max}"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "interference"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode=False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
