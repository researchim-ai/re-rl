# re_rl/tasks/physics/magnetism/magnetism_task.py

"""
MagnetismTask — задачи по магнетизму.

Типы задач:
- lorentz_force: сила Лоренца
- cyclotron: движение заряда в магнитном поле (радиус, период)
- solenoid: магнитное поле соленоида
- ampere_force: сила Ампера
- magnetic_flux: магнитный поток
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


class MagnetismTask(BaseMathTask):
    """Генератор задач по магнетизму."""
    
    TASK_TYPES = [
        "lorentz_force", "cyclotron", "solenoid", 
        "ampere_force", "magnetic_flux"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_B": 0.1, "max_v": 1e5, "max_I": 10},
        2: {"max_B": 0.5, "max_v": 5e5, "max_I": 20},
        3: {"max_B": 1.0, "max_v": 1e6, "max_I": 50},
        4: {"max_B": 2.0, "max_v": 5e6, "max_I": 100},
        5: {"max_B": 5.0, "max_v": 1e7, "max_I": 200},
        6: {"max_B": 10.0, "max_v": 5e7, "max_I": 500},
        7: {"max_B": 20.0, "max_v": 1e8, "max_I": 1000},
        8: {"max_B": 50.0, "max_v": 2e8, "max_I": 2000},
        9: {"max_B": 100.0, "max_v": 2.5e8, "max_I": 5000},
        10: {"max_B": 200.0, "max_v": 2.9e8, "max_I": 10000},
    }
    
    def __init__(
        self,
        task_type: str = "lorentz_force",
        B: float = None,
        v: float = None,
        q: float = None,
        m: float = None,
        angle: float = None,
        I: float = None,
        L: float = None,
        n: int = None,
        S: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.language = language
        
        self.e = get_constant("e")
        self.m_e = get_constant("m_e")
        self.mu_0 = get_constant("mu_0")
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.B = B if B is not None else round(random.uniform(0.01, preset["max_B"]), 3)
        self.v = v if v is not None else random.uniform(1e4, preset["max_v"])
        self.q = q if q is not None else self.e
        self.m = m if m is not None else self.m_e
        self.angle = angle if angle is not None else random.choice([30, 45, 60, 90])
        self.I = I if I is not None else random.uniform(1, preset["max_I"])
        self.L = L if L is not None else random.uniform(0.01, 1.0)
        self.n = n if n is not None else random.randint(100, 5000)
        self.S = S if S is not None else random.uniform(0.001, 0.1)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _format_scientific(self, value: float, precision: int = 3) -> str:
        if abs(value) < 1e-3 or abs(value) > 1e6:
            return f"{value:.{precision}e}"
        return f"{value:.{precision}f}"
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("magnetism", {}).get("problem", {})
        
        if self.task_type == "lorentz_force":
            template = templates.get("lorentz_force", {}).get(self.language, "")
            return template.format(
                q=self._format_scientific(self.q),
                v=self._format_scientific(self.v),
                B=self.B,
                angle=self.angle
            )
        elif self.task_type == "cyclotron":
            template = templates.get("cyclotron", {}).get(self.language, "")
            return template.format(
                m=self._format_scientific(self.m),
                q=self._format_scientific(self.q),
                v=self._format_scientific(self.v),
                B=self.B
            )
        elif self.task_type == "solenoid":
            template = templates.get("solenoid", {}).get(self.language, "")
            return template.format(n=self.n, I=self.I, L=self.L)
        elif self.task_type == "ampere_force":
            template = templates.get("ampere_force", {}).get(self.language, "")
            return template.format(I=self.I, L=self.L, B=self.B, angle=self.angle)
        elif self.task_type == "magnetic_flux":
            template = templates.get("magnetic_flux", {}).get(self.language, "")
            return template.format(B=self.B, S=self.S, angle=self.angle)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("magnetism", {}).get("steps", {})
        
        if self.task_type == "lorentz_force":
            F = self.q * self.v * self.B * math.sin(math.radians(self.angle))
            step1 = templates.get("lorentz_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"F = {self._format_scientific(self.q)} × {self._format_scientific(self.v)} × "
                f"{self.B} × sin({self.angle}°) = {self._format_scientific(F)} Н"
            )
            self.final_answer = f"{self._format_scientific(F)} Н"
        
        elif self.task_type == "cyclotron":
            r = self.m * self.v / (self.q * self.B)
            T = 2 * math.pi * self.m / (self.q * self.B)
            step1 = templates.get("cyclotron_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"r = mv/(qB) = {self._format_scientific(r)} м")
            self.solution_steps.append(f"T = 2πm/(qB) = {self._format_scientific(T)} с")
            self.final_answer = f"r = {self._format_scientific(r)} м, T = {self._format_scientific(T)} с"
        
        elif self.task_type == "solenoid":
            n_per_m = self.n / self.L
            B = self.mu_0 * n_per_m * self.I
            step1 = templates.get("solenoid_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"n = N/L = {self.n}/{self.L} = {n_per_m:.0f} вит/м")
            self.solution_steps.append(f"B = μ₀nI = {self._format_scientific(B)} Тл")
            self.final_answer = f"B = {self._format_scientific(B)} Тл"
        
        elif self.task_type == "ampere_force":
            F = self.B * self.I * self.L * math.sin(math.radians(self.angle))
            step1 = templates.get("ampere_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"F = BIL·sin(α) = {self.B}×{self.I}×{self.L}×sin({self.angle}°) = {F:.4f} Н")
            self.final_answer = f"{F:.4f} Н"
        
        elif self.task_type == "magnetic_flux":
            Phi = self.B * self.S * math.cos(math.radians(self.angle))
            step1 = templates.get("flux_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"Φ = BS·cos(α) = {self.B}×{self.S}×cos({self.angle}°) = {Phi:.6f} Вб")
            self.final_answer = f"{Phi:.6f} Вб"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "magnetism"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
