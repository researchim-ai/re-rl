# re_rl/tasks/physics/mechanics/energy_task.py

"""
EnergyTask — задачи на работу, энергию и мощность.
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.units import format_with_units


class EnergyTask(BaseMathTask):
    """Генератор задач на работу, энергию и мощность."""
    
    TASK_TYPES = [
        "work", "work_angle", "kinetic_energy", 
        "potential_energy", "power", "conservation"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_F": 50, "max_s": 20, "max_m": 10, "max_v": 10, "max_h": 10},
        2: {"max_F": 100, "max_s": 50, "max_m": 20, "max_v": 20, "max_h": 20},
        3: {"max_F": 200, "max_s": 100, "max_m": 30, "max_v": 30, "max_h": 30},
        4: {"max_F": 300, "max_s": 150, "max_m": 50, "max_v": 40, "max_h": 50},
        5: {"max_F": 500, "max_s": 200, "max_m": 50, "max_v": 50, "max_h": 50},
        6: {"max_F": 500, "max_s": 300, "max_m": 100, "max_v": 60, "max_h": 100},
        7: {"max_F": 1000, "max_s": 500, "max_m": 100, "max_v": 80, "max_h": 100},
        8: {"max_F": 1000, "max_s": 500, "max_m": 200, "max_v": 100, "max_h": 200},
        9: {"max_F": 2000, "max_s": 1000, "max_m": 200, "max_v": 150, "max_h": 200},
        10: {"max_F": 5000, "max_s": 1000, "max_m": 500, "max_v": 200, "max_h": 500},
    }
    
    def __init__(
        self,
        task_type: str = "work",
        F: float = None,
        s: float = None,
        angle: float = None,
        m: float = None,
        v: float = None,
        h: float = None,
        W: float = None,
        t: float = None,
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
        self.language = language
        self._reasoning_mode = reasoning_mode
        self.g = get_constant("g")
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.F = F if F is not None else random.randint(10, preset["max_F"])
        self.s = s if s is not None else random.randint(5, preset["max_s"])
        self.angle = angle if angle is not None else random.choice([0, 30, 45, 60])
        self.m = m if m is not None else random.randint(1, preset["max_m"])
        self.v = v if v is not None else random.randint(5, preset["max_v"])
        self.h = h if h is not None else random.randint(5, preset["max_h"])
        self.W = W if W is not None else random.randint(100, 10000)
        self.t = t if t is not None else random.randint(1, 60)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("energy", {}).get("problem", {})
        
        if self.task_type == "work":
            template = templates.get("work", {}).get(self.language, "")
            return template.format(F=self.F, s=self.s)
        elif self.task_type == "work_angle":
            template = templates.get("work_angle", {}).get(self.language, "")
            return template.format(F=self.F, angle=self.angle, s=self.s)
        elif self.task_type == "kinetic_energy":
            template = templates.get("kinetic_energy", {}).get(self.language, "")
            return template.format(m=self.m, v=self.v)
        elif self.task_type == "potential_energy":
            template = templates.get("potential_energy", {}).get(self.language, "")
            return template.format(m=self.m, h=self.h, g=self.g)
        elif self.task_type == "power":
            template = templates.get("power", {}).get(self.language, "")
            return template.format(W=self.W, t=self.t)
        elif self.task_type == "conservation":
            template = templates.get("conservation", {}).get(self.language, "")
            return template.format(m=self.m, h=self.h, g=self.g)
        return ""
    
    def solve(self):
        self.solution_steps = []
        
        if self.task_type == "work":
            W = self.F * self.s
            if self.reasoning_mode:
                self.add_given({"F": self.F, "s": self.s}, {"F": "Н", "s": "м"})
                self.add_find("A", "работа силы" if self.language == "ru" else "work done")
            self.add_formula("A = F·s·cos(α)")
            self.add_substitution(f"A = {self.F} × {self.s} × cos(0°)")
            self.add_calculation(f"{self.F} × {self.s} × 1", W, "Дж")
            if self.reasoning_mode:
                self.add_dimension_check("[Н] × [м] = [Дж] ✓")
            self.final_answer = format_with_units(W, "J", self.language)
        
        elif self.task_type == "work_angle":
            cos_angle = math.cos(math.radians(self.angle))
            W = self.F * self.s * cos_angle
            if self.reasoning_mode:
                self.add_given({"F": self.F, "s": self.s, "α": self.angle}, {"F": "Н", "s": "м", "α": "°"})
                self.add_find("A", "работа силы" if self.language == "ru" else "work done")
            self.add_formula("A = F·s·cos(α)")
            self.add_substitution(f"A = {self.F} × {self.s} × cos({self.angle}°)")
            self.add_calculation(f"{self.F} × {self.s} × {round(cos_angle, 4)}", round(W, 4), "Дж")
            self.final_answer = format_with_units(W, "J", self.language)
        
        elif self.task_type == "kinetic_energy":
            Ek = self.m * self.v ** 2 / 2
            if self.reasoning_mode:
                self.add_given({"m": self.m, "v": self.v}, {"m": "кг", "v": "м/с"})
                self.add_find("Eₖ", "кинетическая энергия" if self.language == "ru" else "kinetic energy")
            self.add_formula("Eₖ = mv²/2")
            self.add_substitution(f"Eₖ = {self.m} × {self.v}² / 2")
            self.add_calculation(f"{self.m} × {self.v**2} / 2", round(Ek, 4), "Дж")
            if self.reasoning_mode:
                self.add_dimension_check("[кг] × [м/с]² = [кг·м²/с²] = [Дж] ✓")
            self.final_answer = format_with_units(Ek, "J", self.language)
        
        elif self.task_type == "potential_energy":
            Ep = self.m * self.g * self.h
            if self.reasoning_mode:
                self.add_given({"m": self.m, "g": self.g, "h": self.h}, {"m": "кг", "g": "м/с²", "h": "м"})
                self.add_find("Eₚ", "потенциальная энергия" if self.language == "ru" else "potential energy")
            self.add_formula("Eₚ = mgh")
            self.add_substitution(f"Eₚ = {self.m} × {self.g} × {self.h}")
            self.add_calculation(f"{self.m} × {self.g} × {self.h}", round(Ep, 4), "Дж")
            if self.reasoning_mode:
                self.add_dimension_check("[кг] × [м/с²] × [м] = [Дж] ✓")
            self.final_answer = format_with_units(Ep, "J", self.language)
        
        elif self.task_type == "power":
            P = self.W / self.t
            if self.reasoning_mode:
                self.add_given({"A": self.W, "t": self.t}, {"A": "Дж", "t": "с"})
                self.add_find("P", "мощность" if self.language == "ru" else "power")
            self.add_formula("P = A/t")
            self.add_substitution(f"P = {self.W} / {self.t}")
            self.add_calculation(f"{self.W}/{self.t}", round(P, 4), "Вт")
            if self.reasoning_mode:
                self.add_dimension_check("[Дж]/[с] = [Вт] ✓")
            self.final_answer = format_with_units(P, "W", self.language)
        
        elif self.task_type == "conservation":
            v = math.sqrt(2 * self.g * self.h)
            if self.reasoning_mode:
                self.add_given({"m": self.m, "h": self.h, "g": self.g}, {"m": "кг", "h": "м", "g": "м/с²"})
                self.add_find("v", "скорость при падении" if self.language == "ru" else "velocity when falling")
                self.add_analysis("По закону сохранения энергии: mgh = mv²/2" if self.language == "ru" else "By energy conservation: mgh = mv²/2")
            self.add_formula("mgh = mv²/2 → v = √(2gh)")
            self.add_substitution(f"v = √(2 × {self.g} × {self.h})")
            self.add_calculation(f"√({2 * self.g * self.h:.2f})", round(v, 4), "м/с")
            self.final_answer = format_with_units(v, "m/s", self.language)
    
    def get_task_type(self) -> str:
        return "energy"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
