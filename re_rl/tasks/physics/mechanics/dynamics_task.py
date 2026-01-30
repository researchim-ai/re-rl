# re_rl/tasks/physics/mechanics/dynamics_task.py

"""
DynamicsTask — задачи по динамике (законы Ньютона).
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
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
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.language = language
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
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
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
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
        
        if self.task_type == "newton_second":
            a = self.F / self.m
            if self.reasoning_mode:
                self.add_given({"F": self.F, "m": self.m}, {"F": "Н", "m": "кг"})
                self.add_find("a", "ускорение" if self.language == "ru" else "acceleration")
                self.add_analysis("Применим второй закон Ньютона." if self.language == "ru" else "Apply Newton's second law.")
            self.add_formula("F = ma → a = F/m")
            self.add_substitution(f"a = {self.F} / {self.m}")
            self.add_calculation(f"{self.F}/{self.m}", round(a, 4), "м/с²")
            if self.reasoning_mode:
                self.add_dimension_check("[Н]/[кг] = [кг·м/с²]/[кг] = [м/с²] ✓")
            self.final_answer = format_with_units(a, "m/s^2", self.language)
        
        elif self.task_type == "find_force":
            F = self.m * self.a
            if self.reasoning_mode:
                self.add_given({"m": self.m, "a": self.a}, {"m": "кг", "a": "м/с²"})
                self.add_find("F", "сила" if self.language == "ru" else "force")
            self.add_formula("F = ma")
            self.add_substitution(f"F = {self.m} × {self.a}")
            self.add_calculation(f"{self.m} × {self.a}", round(F, 4), "Н")
            if self.reasoning_mode:
                self.add_dimension_check("[кг] × [м/с²] = [Н] ✓")
            self.final_answer = format_with_units(F, "N", self.language)
        
        elif self.task_type == "weight":
            W = self.m * self.g
            if self.reasoning_mode:
                self.add_given({"m": self.m, "g": self.g}, {"m": "кг", "g": "м/с²"})
                self.add_find("P", "вес тела" if self.language == "ru" else "weight")
            self.add_formula("P = mg")
            self.add_substitution(f"P = {self.m} × {self.g}")
            self.add_calculation(f"{self.m} × {self.g}", round(W, 4), "Н")
            self.final_answer = format_with_units(W, "N", self.language)
        
        elif self.task_type == "friction":
            N = self.m * self.g
            F_friction = self.mu * N
            if self.reasoning_mode:
                self.add_given({"m": self.m, "μ": self.mu, "g": self.g}, {"m": "кг", "μ": "", "g": "м/с²"})
                self.add_find("F_тр", "сила трения" if self.language == "ru" else "friction force")
                self.add_analysis("Сила трения F_тр = μN, где N — сила нормальной реакции." if self.language == "ru" else "Friction force F_fr = μN, where N is the normal force.")
            self.add_formula("N = mg, F_тр = μN")
            self.add_substitution(f"N = {self.m} × {self.g} = {round(N, 2)} Н")
            self.add_substitution(f"F_тр = {self.mu} × {round(N, 2)}")
            self.add_calculation(f"{self.mu} × {round(N, 2)}", round(F_friction, 4), "Н")
            self.final_answer = format_with_units(F_friction, "N", self.language)
        
        elif self.task_type == "inclined_plane":
            angle_rad = math.radians(self.angle)
            F_parallel = self.m * self.g * math.sin(angle_rad)
            if self.reasoning_mode:
                self.add_given({"m": self.m, "θ": self.angle, "g": self.g}, {"m": "кг", "θ": "°", "g": "м/с²"})
                self.add_find("F", "сила вдоль плоскости" if self.language == "ru" else "force along the plane")
                self.add_analysis("Разложим силу тяжести на составляющие." if self.language == "ru" else "Decompose gravity into components.")
            self.add_formula("F = mg·sin(θ)")
            self.add_substitution(f"F = {self.m} × {self.g} × sin({self.angle}°)")
            self.add_calculation(f"{self.m} × {self.g} × {round(math.sin(angle_rad), 4)}", round(F_parallel, 4), "Н")
            self.final_answer = format_with_units(F_parallel, "N", self.language)
        
        elif self.task_type == "tension":
            T = 2 * self.m1 * self.m2 * self.g / (self.m1 + self.m2)
            if self.reasoning_mode:
                self.add_given({"m₁": self.m1, "m₂": self.m2, "g": self.g}, {"m₁": "кг", "m₂": "кг", "g": "м/с²"})
                self.add_find("T", "натяжение нити" if self.language == "ru" else "string tension")
                self.add_analysis("Система Атвуда. Из законов Ньютона для обоих тел выводим формулу натяжения." if self.language == "ru" else "Atwood machine. From Newton's laws for both bodies we derive the tension formula.")
            self.add_formula("T = 2m₁m₂g/(m₁+m₂)")
            self.add_substitution(f"T = 2 × {self.m1} × {self.m2} × {self.g} / ({self.m1} + {self.m2})")
            self.add_calculation(f"{2*self.m1*self.m2*self.g}/{self.m1+self.m2}", round(T, 4), "Н")
            self.final_answer = format_with_units(T, "N", self.language)
    
    def get_task_type(self) -> str:
        return "dynamics"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru", 
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language, 
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
