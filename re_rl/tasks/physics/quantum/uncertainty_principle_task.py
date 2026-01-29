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

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        self.dx = round(random.uniform(0.01, 1), 3)  # нм
        self.tau = random.uniform(1e-10, 1e-6)  # с (время жизни)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

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
            steps.append(f"Δp ≥ ħ/(2Δx) = {self.h_bar:.3e}/(2·{dx_m:.3e}) = {dp:.4e} кг·м/с")
            answer = f"Δp ≥ {dp:.4e} кг·м/с"
        elif self.task_type == "energy_time":
            steps.append(t["steps"]["energy_time"][self.language])
            dE = self.h_bar / (2 * self.tau)
            dE_eV = dE / self.eV
            steps.append(f"ΔE ≥ ħ/(2τ) = {self.h_bar:.3e}/(2·{self.tau:.2e}) = {dE:.4e} Дж")
            steps.append(f"ΔE = {dE_eV:.4e} эВ")
            answer = f"ΔE ≥ {dE_eV:.4e} эВ"
        else:
            steps.append(t["steps"]["position_momentum"][self.language])
            steps.append("Минимизируем энергию E = p²/(2m) + U(r)")
            # Оценка: r ~ ħ/(m_e·v), p ~ m_e·v
            # E ~ ħ²/(2m_e·r²) - e²/(4πε₀·r)
            # Минимум при r ~ a₀
            a0 = 5.29e-11  # м (боровский радиус)
            steps.append(f"r_min ≈ ħ²/(m_e·e²·k) ≈ a₀ = {a0*1e9:.4f} нм = 0.529 Å")
            answer = f"r ≈ 0.529 Å (боровский радиус)"
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "uncertainty_principle"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
