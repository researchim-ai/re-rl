from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/quantum/uncertainty_principle_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class UncertaintyPrincipleTask(BaseMathTask):
    """Задачи на принцип неопределённости Гейзенберга."""
    
    TASK_TYPES = ["position_momentum", "energy_time", "atom_size"]
    
    h_bar = 1.055e-34  # Дж·с (ħ)
    h = 6.626e-34  # Дж·с
    m_e = 9.109e-31  # кг
    eV = 1.602e-19  # Дж

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text", reasoning_mode: bool = False):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.dx = round(random.uniform(0.01, 1), 3)  # нм
        self.tau = random.uniform(1e-10, 1e-6)  # с (время жизни)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["uncertainty_principle"]
        text = t["instructions"][self.language] + "\n\n"
        
        if self.task_type == "position_momentum":
            text += t["problem"]["position_momentum"][self.language].format(dx=self.dx)
        elif self.task_type == "energy_time":
            text += t["problem"]["energy_time"][self.language].format(tau=f"{self.tau:.2e}")
        else:
            text += t["problem"]["atom_size"][self.language]
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["uncertainty_principle"]
        steps = []
        
        if self.task_type == "position_momentum":
            steps.append(t["steps"]["position_momentum"][self.language])
            steps.append(t["steps"]["min_uncertainty"][self.language])
            dx_m = self.dx * 1e-9
            dp = self.h_bar / (2 * dx_m)
            steps.append(texts.t('s1', self.language, h_bar=self.h_bar, dx_m=dx_m, dp=dp))
            answer = texts.t('s0', self.language, dp=dp)
        elif self.task_type == "energy_time":
            steps.append(t["steps"]["energy_time"][self.language])
            dE = self.h_bar / (2 * self.tau)
            dE_eV = dE / self.eV
            steps.append(texts.t('s4', self.language, h_bar=self.h_bar, tau=self.tau, dE=dE))
            steps.append(texts.t('s5', self.language, dE_eV=dE_eV))
            answer = texts.t('s2', self.language, dE_eV=dE_eV)
        else:
            steps.append(t["steps"]["position_momentum"][self.language])
            steps.append(texts.t('s6', self.language))
            # Оценка: r ~ ħ/(m_e·v), p ~ m_e·v
            # E ~ ħ²/(2m_e·r²) - e²/(4πε₀·r)
            # Минимум при r ~ a₀
            a0 = 5.29e-11  # м (боровский радиус)
            steps.append(texts.t('s7', self.language, v0=a0 * 1000000000.0))
            answer = texts.t('s3', self.language)
        
        self.solution_steps = steps
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "uncertainty_principle"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
