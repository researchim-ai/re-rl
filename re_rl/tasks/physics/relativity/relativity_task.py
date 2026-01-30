# re_rl/tasks/physics/relativity/relativity_task.py

"""
RelativityTask — задачи по специальной теории относительности.

Типы задач:
- time_dilation: замедление времени
- length_contraction: сокращение длины
- mass_energy: E = mc²
- relativistic_momentum: релятивистский импульс
- lorentz_factor: фактор Лоренца
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


class RelativityTask(BaseMathTask):
    """Генератор задач по СТО."""
    
    TASK_TYPES = [
        "time_dilation", "length_contraction", "mass_energy",
        "relativistic_momentum", "lorentz_factor"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_beta": 0.3, "max_m": 1},
        2: {"max_beta": 0.5, "max_m": 10},
        3: {"max_beta": 0.6, "max_m": 100},
        4: {"max_beta": 0.7, "max_m": 1000},
        5: {"max_beta": 0.8, "max_m": 10000},
        6: {"max_beta": 0.85, "max_m": 100000},
        7: {"max_beta": 0.9, "max_m": 1e6},
        8: {"max_beta": 0.95, "max_m": 1e7},
        9: {"max_beta": 0.99, "max_m": 1e8},
        10: {"max_beta": 0.999, "max_m": 1e9},
    }
    
    def __init__(
        self,
        task_type: str = "time_dilation",
        v: float = None,
        beta: float = None,
        t0: float = None,
        L0: float = None,
        m: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.language = language
        
        self.c = get_constant("c")
        
        preset = self._interpolate_difficulty(difficulty)
        
        # β = v/c
        self.beta = beta if beta is not None else round(random.uniform(0.1, preset["max_beta"]), 3)
        self.v = v if v is not None else self.beta * self.c
        self.t0 = t0 if t0 is not None else random.uniform(1, 100)
        self.L0 = L0 if L0 is not None else random.uniform(1, 1000)
        self.m = m if m is not None else random.uniform(0.001, preset["max_m"])
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _lorentz_factor(self) -> float:
        """γ = 1/√(1 - β²)"""
        return 1 / math.sqrt(1 - self.beta ** 2)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("relativity", {}).get("problem", {})
        
        if self.task_type == "time_dilation":
            template = templates.get("time_dilation", {}).get(self.language, "")
            return template.format(t0=self.t0, beta=self.beta)
        elif self.task_type == "length_contraction":
            template = templates.get("length_contraction", {}).get(self.language, "")
            return template.format(L0=self.L0, beta=self.beta)
        elif self.task_type == "mass_energy":
            template = templates.get("mass_energy", {}).get(self.language, "")
            return template.format(m=self.m)
        elif self.task_type == "relativistic_momentum":
            template = templates.get("relativistic_momentum", {}).get(self.language, "")
            return template.format(m=self.m, beta=self.beta)
        elif self.task_type == "lorentz_factor":
            template = templates.get("lorentz_factor", {}).get(self.language, "")
            return template.format(beta=self.beta)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("relativity", {}).get("steps", {})
        
        gamma = self._lorentz_factor()
        
        if self.task_type == "time_dilation":
            t = self.t0 * gamma
            step1 = templates.get("time_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"γ = 1/√(1 - {self.beta}²) = {gamma:.4f}")
            self.solution_steps.append(f"t = t₀·γ = {self.t0} × {gamma:.4f} = {t:.4f} с")
            self.final_answer = f"t = {t:.4f} с"
        
        elif self.task_type == "length_contraction":
            L = self.L0 / gamma
            step1 = templates.get("length_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"γ = {gamma:.4f}")
            self.solution_steps.append(f"L = L₀/γ = {self.L0} / {gamma:.4f} = {L:.4f} м")
            self.final_answer = f"L = {L:.4f} м"
        
        elif self.task_type == "mass_energy":
            E = self.m * self.c ** 2
            E_joules = E
            E_eV = E / get_constant("e")
            step1 = templates.get("mass_energy_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"E = mc² = {self.m} × ({self.c})²")
            self.solution_steps.append(f"E = {E_joules:.4e} Дж = {E_eV:.4e} эВ")
            self.final_answer = f"E = {E_joules:.4e} Дж"
        
        elif self.task_type == "relativistic_momentum":
            p = gamma * self.m * self.v
            step1 = templates.get("momentum_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"γ = {gamma:.4f}")
            self.solution_steps.append(f"p = γmv = {gamma:.4f} × {self.m} × {self.v:.4e} = {p:.4e} кг·м/с")
            self.final_answer = f"p = {p:.4e} кг·м/с"
        
        elif self.task_type == "lorentz_factor":
            step1 = templates.get("lorentz_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"γ = 1/√(1 - {self.beta}²) = 1/√(1 - {self.beta**2:.6f})")
            self.solution_steps.append(f"γ = 1/√{1 - self.beta**2:.6f} = {gamma:.6f}")
            self.final_answer = f"γ = {gamma:.6f}"
    
    def get_task_type(self) -> str:
        return "relativity"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
