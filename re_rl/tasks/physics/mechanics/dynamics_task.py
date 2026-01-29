# re_rl/tasks/physics/mechanics/dynamics_task.py

"""
DynamicsTask — задачи по динамике (законы Ньютона).
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.units import format_with_units


class DynamicsTask(BaseMathTask):
    """Генератор задач по динамике."""
    
    TASK_TYPES = [
        "newton_second", "find_force", "weight", 
        "friction", "inclined_plane", "tension"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 10, "max_F": 50, "max_a": 5},
        2: {"max_m": 20, "max_F": 100, "max_a": 10},
        3: {"max_m": 30, "max_F": 200, "max_a": 10},
        4: {"max_m": 50, "max_F": 300, "max_a": 15},
        5: {"max_m": 50, "max_F": 500, "max_a": 15},
        6: {"max_m": 100, "max_F": 500, "max_a": 20},
        7: {"max_m": 100, "max_F": 1000, "max_a": 20},
        8: {"max_m": 200, "max_F": 1000, "max_a": 25},
        9: {"max_m": 200, "max_F": 2000, "max_a": 25},
        10: {"max_m": 500, "max_F": 5000, "max_a": 30},
    }
    
    def __init__(
        self,
        task_type: str = "newton_second",
        m: float = None,
        m1: float = None,
        m2: float = None,
        F: float = None,
        a: float = None,
        mu: float = None,
        angle: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.language = language
        self.g = get_constant("g")
        
        preset = self._interpolate_difficulty(difficulty)
        max_m = preset.get("max_m", 50)
        max_F = preset.get("max_F", 500)
        max_a = preset.get("max_a", 15)
        
        self.m = m if m is not None else random.randint(1, max_m)
        self.m1 = m1 if m1 is not None else random.randint(1, max_m)
        self.m2 = m2 if m2 is not None else random.randint(1, max_m)
        self.F = F if F is not None else random.randint(10, max_F)
        self.a = a if a is not None else random.randint(1, max_a)
        self.mu = mu if mu is not None else round(random.uniform(0.1, 0.5), 2)
        self.angle = angle if angle is not None else random.choice([15, 30, 45, 60])
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("dynamics", {}).get("problem", {})
        
        if self.task_type == "newton_second":
            template = templates.get("newton_second", {}).get(self.language, "")
            return template.format(m=self.m, F=self.F)
        elif self.task_type == "find_force":
            template = templates.get("find_force", {}).get(self.language, "")
            return template.format(m=self.m, a=self.a)
        elif self.task_type == "weight":
            template = templates.get("weight", {}).get(self.language, "")
            return template.format(m=self.m, g=self.g)
        elif self.task_type == "friction":
            template = templates.get("friction", {}).get(self.language, "")
            return template.format(m=self.m, mu=self.mu, g=self.g)
        elif self.task_type == "inclined_plane":
            template = templates.get("inclined_plane", {}).get(self.language, "")
            return template.format(m=self.m, angle=self.angle, g=self.g)
        elif self.task_type == "tension":
            template = templates.get("tension", {}).get(self.language, "")
            return template.format(m1=self.m1, m2=self.m2, g=self.g)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("dynamics", {}).get("steps", {})
        
        if self.task_type == "newton_second":
            # a = F/m
            a = self.F / self.m
            step1 = templates.get("apply_newton", {}).get(self.language, "")
            self.solution_steps.append(step1.format(step=1))
            step2 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step2.format(step=2, calculation=f"a = F/m = {self.F}/{self.m} = {a:.4f}"))
            self.final_answer = format_with_units(a, "m/s^2", self.language)
        
        elif self.task_type == "find_force":
            F = self.m * self.a
            step1 = templates.get("apply_newton", {}).get(self.language, "")
            self.solution_steps.append(step1.format(step=1))
            step2 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step2.format(step=2, calculation=f"F = ma = {self.m} × {self.a} = {F:.4f}"))
            self.final_answer = format_with_units(F, "N", self.language)
        
        elif self.task_type == "weight":
            W = self.m * self.g
            step1 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step1.format(step=1, calculation=f"P = mg = {self.m} × {self.g} = {W:.4f}"))
            self.final_answer = format_with_units(W, "N", self.language)
        
        elif self.task_type == "friction":
            N = self.m * self.g
            F_friction = self.mu * N
            step1 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step1.format(step=1, calculation=f"N = mg = {self.m} × {self.g} = {N:.4f} Н"))
            step2 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step2.format(step=2, calculation=f"F_тр = μN = {self.mu} × {N:.4f} = {F_friction:.4f}"))
            self.final_answer = format_with_units(F_friction, "N", self.language)
        
        elif self.task_type == "inclined_plane":
            angle_rad = math.radians(self.angle)
            F_parallel = self.m * self.g * math.sin(angle_rad)
            step1 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step1.format(
                step=1, 
                calculation=f"F = mg·sin(θ) = {self.m} × {self.g} × sin({self.angle}°) = {F_parallel:.4f}"
            ))
            self.final_answer = format_with_units(F_parallel, "N", self.language)
        
        elif self.task_type == "tension":
            # Атвуда машина: a = (m2-m1)g/(m1+m2), T = 2m1m2g/(m1+m2)
            if self.m2 > self.m1:
                T = 2 * self.m1 * self.m2 * self.g / (self.m1 + self.m2)
            else:
                T = 2 * self.m1 * self.m2 * self.g / (self.m1 + self.m2)
            step1 = templates.get("calculate_result", {}).get(self.language, "")
            self.solution_steps.append(step1.format(
                step=1,
                calculation=f"T = 2m₁m₂g/(m₁+m₂) = 2×{self.m1}×{self.m2}×{self.g}/({self.m1}+{self.m2}) = {T:.4f}"
            ))
            self.final_answer = format_with_units(T, "N", self.language)
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "dynamics"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru", 
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language, 
                  detail_level=detail_level, difficulty=difficulty)
