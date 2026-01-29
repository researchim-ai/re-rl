# re_rl/tasks/physics/quantum/de_broglie_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class DeBroglieTask(BaseMathTask):
    """Задачи на волны де Бройля."""
    
    TASK_TYPES = ["wavelength", "electron_velocity", "momentum"]
    
    PARTICLES = {
        "electron": {"mass": 9.109e-31, "name_ru": "электрона", "name_en": "electron"},
        "proton": {"mass": 1.673e-27, "name_ru": "протона", "name_en": "proton"},
        "neutron": {"mass": 1.675e-27, "name_ru": "нейтрона", "name_en": "neutron"},
    }
    
    h = 6.626e-34  # Дж·с
    eV = 1.602e-19  # Дж

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.particle = random.choice(list(self.PARTICLES.keys()))
        self.E = round(random.uniform(10, 1000), 0)  # эВ
        self.U = round(random.uniform(10, 500), 0)  # В
        self.wavelength = round(random.uniform(100, 700), 0)  # нм
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["de_broglie"]
        text = t["instructions"][self.language] + "\n\n"
        
        particle_name = t["particles"][self.particle][self.language]
        
        if self.task_type == "wavelength":
            text += t["problem"]["wavelength"][self.language].format(particle=particle_name, E=self.E)
        elif self.task_type == "electron_velocity":
            text += t["problem"]["electron_velocity"][self.language].format(U=self.U)
        else:
            text += t["problem"]["momentum"][self.language].format(**{"lambda": self.wavelength})
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["de_broglie"]
        steps = []
        
        if self.task_type == "wavelength":
            steps.append(t["steps"]["de_broglie"][self.language])
            m = self.PARTICLES[self.particle]["mass"]
            E_J = self.E * self.eV
            wavelength = self.h / math.sqrt(2 * m * E_J)
            steps.append(f"λ = h/√(2mE) = {self.h:.3e}/√(2·{m:.3e}·{E_J:.3e})")
            steps.append(f"λ = {wavelength:.4e} м = {wavelength*1e12:.4f} пм")
            answer = f"λ = {wavelength*1e12:.4f} пм"
        elif self.task_type == "electron_velocity":
            steps.append(t["steps"]["electron_accelerated"][self.language])
            m_e = self.PARTICLES["electron"]["mass"]
            wavelength = self.h / math.sqrt(2 * m_e * self.eV * self.U)
            approx = 1.226 / math.sqrt(self.U)
            steps.append(f"λ ≈ 1.226/√{self.U} = {round(approx, 4)} нм")
            steps.append(f"Точно: λ = {wavelength*1e9:.6f} нм")
            answer = f"λ = {round(approx, 4)} нм"
        else:
            steps.append(t["steps"]["photon_momentum"][self.language])
            lambda_m = self.wavelength * 1e-9
            p = self.h / lambda_m
            steps.append(f"p = h/λ = {self.h:.3e}/{lambda_m:.3e} = {p:.4e} кг·м/с")
            answer = f"p = {p:.4e} кг·м/с"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "de_broglie"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
