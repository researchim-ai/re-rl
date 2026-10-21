from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

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
        "electron": {"mass": 9.109e-31, "name_ru": texts.literal('literals.s0'), "name_en": "electron"},
        "proton": {"mass": 1.673e-27, "name_ru": texts.literal('literals.s1'), "name_en": "proton"},
        "neutron": {"mass": 1.675e-27, "name_ru": texts.literal('literals.s2'), "name_en": "neutron"},
    }
    
    h = 6.626e-34  # Дж·с
    eV = 1.602e-19  # Дж

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode: bool = False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.particle = random.choice(list(self.PARTICLES.keys()))
        self.E = round(random.uniform(10, 1000), 0)  # эВ
        self.U = round(random.uniform(10, 500), 0)  # В
        self.wavelength = round(random.uniform(100, 700), 0)  # нм
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

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
            steps.append(texts.t('s4', self.language, wavelength=wavelength, v1=wavelength * 1000000000000.0))
            answer = texts.t('s3', self.language, v0=wavelength * 1000000000000.0)
        elif self.task_type == "electron_velocity":
            steps.append(t["steps"]["electron_accelerated"][self.language])
            m_e = self.PARTICLES["electron"]["mass"]
            wavelength = self.h / math.sqrt(2 * m_e * self.eV * self.U)
            approx = 1.226 / math.sqrt(self.U)
            steps.append(texts.t('s7', self.language, U=self.U, v1=round(approx, 4)))
            steps.append(texts.t('s8', self.language, v0=wavelength * 1000000000.0))
            answer = texts.t('s5', self.language, v0=round(approx, 4))
        else:
            steps.append(t["steps"]["photon_momentum"][self.language])
            lambda_m = self.wavelength * 1e-9
            p = self.h / lambda_m
            steps.append(texts.t('s9', self.language, h=self.h, lambda_m=lambda_m, p=p))
            answer = texts.t('s6', self.language, p=p)
        
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "de_broglie"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
