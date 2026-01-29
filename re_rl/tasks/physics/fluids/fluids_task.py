# re_rl/tasks/physics/fluids/fluids_task.py

"""
FluidsTask — задачи по гидростатике и гидродинамике.

Типы задач:
- pressure: давление жидкости
- archimedes: закон Архимеда
- bernoulli: уравнение Бернулли
- continuity: уравнение непрерывности
- pascal: закон Паскаля
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


# Плотности веществ (кг/м³)
DENSITIES = {
    "water": 1000,
    "oil": 900,
    "mercury": 13600,
    "alcohol": 800,
    "seawater": 1025,
    "iron": 7874,
    "aluminum": 2700,
    "wood": 600,
    "ice": 917,
}


class FluidsTask(BaseMathTask):
    """Генератор задач по гидростатике."""
    
    TASK_TYPES = [
        "pressure", "archimedes", "bernoulli", "continuity", "pascal"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_h": 5, "max_V": 0.1, "max_v": 5},
        2: {"max_h": 10, "max_V": 0.5, "max_v": 10},
        3: {"max_h": 20, "max_V": 1, "max_v": 20},
        4: {"max_h": 50, "max_V": 5, "max_v": 30},
        5: {"max_h": 100, "max_V": 10, "max_v": 50},
        6: {"max_h": 200, "max_V": 50, "max_v": 100},
        7: {"max_h": 500, "max_V": 100, "max_v": 150},
        8: {"max_h": 1000, "max_V": 500, "max_v": 200},
        9: {"max_h": 5000, "max_V": 1000, "max_v": 300},
        10: {"max_h": 10000, "max_V": 5000, "max_v": 500},
    }
    
    def __init__(
        self,
        task_type: str = "pressure",
        h: float = None,
        rho: float = None,
        fluid: str = None,
        V: float = None,
        m: float = None,
        v1: float = None,
        v2: float = None,
        A1: float = None,
        A2: float = None,
        F1: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self.language = language
        
        self.g = get_constant("g")
        self.P0 = 101325  # Атмосферное давление, Па
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.fluid = fluid or random.choice(list(DENSITIES.keys()))
        self.rho = rho if rho is not None else DENSITIES.get(self.fluid, 1000)
        self.h = h if h is not None else round(random.uniform(0.5, preset["max_h"]), 2)
        self.V = V if V is not None else round(random.uniform(0.001, preset["max_V"]), 4)
        self.m = m if m is not None else round(self.rho * self.V * random.uniform(0.5, 2), 2)
        self.v1 = v1 if v1 is not None else round(random.uniform(1, preset["max_v"]), 2)
        self.v2 = v2 if v2 is not None else round(random.uniform(1, preset["max_v"]), 2)
        self.A1 = A1 if A1 is not None else round(random.uniform(0.001, 0.1), 4)
        self.A2 = A2 if A2 is not None else round(random.uniform(0.0001, self.A1), 4)
        self.F1 = F1 if F1 is not None else round(random.uniform(10, 1000), 1)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _get_fluid_name(self) -> str:
        names = {
            "water": {"ru": "вода", "en": "water"},
            "oil": {"ru": "масло", "en": "oil"},
            "mercury": {"ru": "ртуть", "en": "mercury"},
            "alcohol": {"ru": "спирт", "en": "alcohol"},
            "seawater": {"ru": "морская вода", "en": "seawater"},
        }
        return names.get(self.fluid, {}).get(self.language, self.fluid)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("fluids", {}).get("problem", {})
        
        if self.task_type == "pressure":
            template = templates.get("pressure", {}).get(self.language, "")
            return template.format(fluid=self._get_fluid_name(), h=self.h, rho=self.rho, g=self.g)
        elif self.task_type == "archimedes":
            template = templates.get("archimedes", {}).get(self.language, "")
            return template.format(V=self.V, rho=self.rho, fluid=self._get_fluid_name())
        elif self.task_type == "bernoulli":
            template = templates.get("bernoulli", {}).get(self.language, "")
            return template.format(v1=self.v1, h=self.h, rho=self.rho)
        elif self.task_type == "continuity":
            template = templates.get("continuity", {}).get(self.language, "")
            return template.format(A1=self.A1*1e4, v1=self.v1, A2=self.A2*1e4)  # см²
        elif self.task_type == "pascal":
            template = templates.get("pascal", {}).get(self.language, "")
            return template.format(F1=self.F1, A1=self.A1*1e4, A2=self.A2*1e4)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("fluids", {}).get("steps", {})
        
        if self.task_type == "pressure":
            P = self.rho * self.g * self.h
            P_total = self.P0 + P
            step1 = templates.get("pressure_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"P = ρgh = {self.rho} × {self.g} × {self.h} = {P:.2f} Па")
            self.solution_steps.append(f"P_полн = P₀ + ρgh = {self.P0} + {P:.2f} = {P_total:.2f} Па")
            self.final_answer = f"P = {P:.2f} Па (избыточное), {P_total:.2f} Па (абсолютное)"
        
        elif self.task_type == "archimedes":
            F_a = self.rho * self.g * self.V
            step1 = templates.get("archimedes_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"F_A = ρgV = {self.rho} × {self.g} × {self.V} = {F_a:.4f} Н")
            self.final_answer = f"F_A = {F_a:.4f} Н"
        
        elif self.task_type == "bernoulli":
            # P1 + ρv1²/2 + ρgh1 = P2 + ρv2²/2 + ρgh2
            # При h2=0: v2 = √(v1² + 2gh)
            v2 = math.sqrt(self.v1**2 + 2 * self.g * self.h)
            step1 = templates.get("bernoulli_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"v₂ = √(v₁² + 2gh) = √({self.v1}² + 2×{self.g}×{self.h})")
            self.solution_steps.append(f"v₂ = {v2:.4f} м/с")
            self.final_answer = f"v₂ = {v2:.4f} м/с"
        
        elif self.task_type == "continuity":
            v2 = self.A1 * self.v1 / self.A2
            step1 = templates.get("continuity_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"v₂ = A₁v₁/A₂ = {self.A1*1e4}×{self.v1}/{self.A2*1e4} = {v2:.4f} м/с")
            self.final_answer = f"v₂ = {v2:.4f} м/с"
        
        elif self.task_type == "pascal":
            F2 = self.F1 * self.A2 / self.A1
            step1 = templates.get("pascal_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"F₂/F₁ = A₂/A₁ => F₂ = F₁·A₂/A₁")
            self.solution_steps.append(f"F₂ = {self.F1} × {self.A2*1e4}/{self.A1*1e4} = {F2:.4f} Н")
            self.final_answer = f"F₂ = {F2:.4f} Н"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "fluids"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
