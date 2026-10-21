from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/quantum/bohr_model_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class BohrModelTask(BaseMathTask):
    """Задачи на модель атома Бора."""
    
    TASK_TYPES = ["energy_level", "transition", "orbit_radius", "ionization"]
    
    # Константы
    E1 = -13.6  # эВ (энергия основного состояния)
    a0 = 0.529  # Å (боровский радиус)
    h = 6.626e-34  # Дж·с
    c = 3e8  # м/с
    eV = 1.602e-19  # Дж

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode: bool = False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.n = random.randint(1, 6)  # главное квантовое число
        self.n1 = random.randint(3, 6)  # начальный уровень
        self.n2 = random.randint(1, self.n1 - 1)  # конечный уровень
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["bohr_model"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "energy_level":
            text += t["problem"]["energy_level"][self.language].format(n=self.n)
        elif self.task_type == "transition":
            text += t["problem"]["transition"][self.language].format(n1=self.n1, n2=self.n2)
        elif self.task_type == "orbit_radius":
            text += t["problem"]["orbit_radius"][self.language].format(n=self.n)
        else:
            text += t["problem"]["ionization"][self.language].format(n=self.n)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["bohr_model"]
        steps = []
        
        if self.task_type == "energy_level":
            steps.append(t["steps"]["energy_formula"][self.language])
            E_n = self.E1 / (self.n ** 2)
            steps.append(texts.t('s1', self.language, n=self.n, n_2=self.n, v2=round(E_n, 4)))
            answer = texts.t('s0', self.language, v0=round(E_n, 4))
        elif self.task_type == "transition":
            steps.append(t["steps"]["transition_energy"][self.language])
            dE = self.E1 * (1/self.n2**2 - 1/self.n1**2)
            dE = abs(dE)
            steps.append(texts.t('s3', self.language, n2=self.n2, n1=self.n1, v2=round(dE, 4)))
            steps.append(t["steps"]["wavelength"][self.language])
            # λ = hc/ΔE
            dE_J = dE * self.eV
            wavelength = self.h * self.c / dE_J * 1e9  # в нм
            steps.append(texts.t('s4', self.language, v0=round(wavelength, 1)))
            answer = texts.t('s2', self.language, v0=round(wavelength, 1))
        elif self.task_type == "orbit_radius":
            steps.append(t["steps"]["radius_formula"][self.language])
            r_n = self.n ** 2 * self.a0
            steps.append(texts.t('s6', self.language, n=self.n, n_2=self.n, a0=self.a0, v3=round(r_n, 3), v4=round(r_n * 0.1, 4)))
            answer = f"r = {round(r_n, 3)} Å"
        else:
            steps.append(t["steps"]["energy_formula"][self.language])
            E_n = self.E1 / (self.n ** 2)
            E_ion = abs(E_n)
            steps.append(texts.t('s7', self.language, n=self.n, n_2=self.n, v2=round(E_n, 4)))
            steps.append(texts.t('s8', self.language, n=self.n, v1=round(E_ion, 4)))
            answer = texts.t('s5', self.language, v0=round(E_ion, 4))
        
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "bohr_model"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
