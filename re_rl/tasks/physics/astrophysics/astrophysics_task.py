# re_rl/tasks/physics/astrophysics/astrophysics_task.py

"""
AstrophysicsTask — задачи по астрофизике.

Типы задач:
- orbital_velocity: орбитальная скорость
- escape_velocity: вторая космическая скорость
- kepler_third: третий закон Кеплера
- gravitational_force: сила гравитации
- schwarzschild: радиус Шварцшильда
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant, PHYSICS_CONSTANTS


# Данные о небесных телах
CELESTIAL_BODIES = {
    "Earth": {"M": 5.972e24, "R": 6.371e6, "name_ru": "Земля", "name_en": "Earth"},
    "Moon": {"M": 7.342e22, "R": 1.737e6, "name_ru": "Луна", "name_en": "Moon"},
    "Mars": {"M": 6.417e23, "R": 3.390e6, "name_ru": "Марс", "name_en": "Mars"},
    "Jupiter": {"M": 1.898e27, "R": 6.991e7, "name_ru": "Юпитер", "name_en": "Jupiter"},
    "Sun": {"M": 1.989e30, "R": 6.957e8, "name_ru": "Солнце", "name_en": "Sun"},
}


class AstrophysicsTask(BaseMathTask):
    """Генератор задач по астрофизике."""
    
    TASK_TYPES = [
        "orbital_velocity", "escape_velocity", "kepler_third",
        "gravitational_force", "schwarzschild"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_r_factor": 2, "simple_bodies": True},
        2: {"max_r_factor": 5, "simple_bodies": True},
        3: {"max_r_factor": 10, "simple_bodies": True},
        4: {"max_r_factor": 50, "simple_bodies": False},
        5: {"max_r_factor": 100, "simple_bodies": False},
        6: {"max_r_factor": 500, "simple_bodies": False},
        7: {"max_r_factor": 1000, "simple_bodies": False},
        8: {"max_r_factor": 5000, "simple_bodies": False},
        9: {"max_r_factor": 10000, "simple_bodies": False},
        10: {"max_r_factor": 100000, "simple_bodies": False},
    }
    
    def __init__(
        self,
        task_type: str = "orbital_velocity",
        body: str = None,
        M: float = None,
        R: float = None,
        r: float = None,
        m: float = None,
        T: float = None,
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
        
        self.G = get_constant("G")
        self.c = get_constant("c")
        
        preset = self._interpolate_difficulty(difficulty)
        
        # Выбор небесного тела
        if body and body in CELESTIAL_BODIES:
            self.body = body
        else:
            self.body = random.choice(list(CELESTIAL_BODIES.keys()))
        
        body_data = CELESTIAL_BODIES[self.body]
        self.M = M if M is not None else body_data["M"]
        self.R = R if R is not None else body_data["R"]
        
        # Радиус орбиты
        r_factor = random.uniform(1.1, preset["max_r_factor"])
        self.r = r if r is not None else self.R * r_factor
        
        self.m = m if m is not None else random.uniform(100, 10000)  # Масса спутника, кг
        self.T = T if T is not None else random.uniform(3600, 365*24*3600)  # Период, с
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _get_body_name(self) -> str:
        body_data = CELESTIAL_BODIES.get(self.body, {})
        name_key = "name_ru" if self.language == "ru" else "name_en"
        return body_data.get(name_key, self.body)
    
    def _format_scientific(self, value: float, precision: int = 3) -> str:
        if abs(value) < 1e-3 or abs(value) > 1e6:
            return f"{value:.{precision}e}"
        return f"{value:.{precision}f}"
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("astrophysics", {}).get("problem", {})
        
        if self.task_type == "orbital_velocity":
            template = templates.get("orbital_velocity", {}).get(self.language, "")
            return template.format(
                body=self._get_body_name(),
                r=self._format_scientific(self.r),
                M=self._format_scientific(self.M)
            )
        elif self.task_type == "escape_velocity":
            template = templates.get("escape_velocity", {}).get(self.language, "")
            return template.format(
                body=self._get_body_name(),
                M=self._format_scientific(self.M),
                R=self._format_scientific(self.R)
            )
        elif self.task_type == "kepler_third":
            template = templates.get("kepler_third", {}).get(self.language, "")
            return template.format(
                body=self._get_body_name(),
                T=self.T / 3600,  # В часах
                M=self._format_scientific(self.M)
            )
        elif self.task_type == "gravitational_force":
            template = templates.get("gravitational_force", {}).get(self.language, "")
            return template.format(
                M=self._format_scientific(self.M),
                m=self.m,
                r=self._format_scientific(self.r)
            )
        elif self.task_type == "schwarzschild":
            template = templates.get("schwarzschild", {}).get(self.language, "")
            return template.format(M=self._format_scientific(self.M))
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("astrophysics", {}).get("steps", {})
        
        if self.task_type == "orbital_velocity":
            v = math.sqrt(self.G * self.M / self.r)
            step1 = templates.get("orbital_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"v = √(GM/r) = √({self.G:.4e} × {self.M:.4e} / {self.r:.4e})")
            self.solution_steps.append(f"v = {v:.2f} м/с = {v/1000:.2f} км/с")
            self.final_answer = f"v = {v:.2f} м/с ({v/1000:.2f} км/с)"
        
        elif self.task_type == "escape_velocity":
            v_esc = math.sqrt(2 * self.G * self.M / self.R)
            step1 = templates.get("escape_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"v₂ = √(2GM/R) = √(2 × {self.G:.4e} × {self.M:.4e} / {self.R:.4e})")
            self.solution_steps.append(f"v₂ = {v_esc:.2f} м/с = {v_esc/1000:.2f} км/с")
            self.final_answer = f"v₂ = {v_esc:.2f} м/с ({v_esc/1000:.2f} км/с)"
        
        elif self.task_type == "kepler_third":
            # T² = (4π²/GM) × r³ => r = ∛(GMT²/4π²)
            r = (self.G * self.M * self.T**2 / (4 * math.pi**2)) ** (1/3)
            step1 = templates.get("kepler_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"r = ∛(GMT²/4π²)")
            self.solution_steps.append(f"r = {r:.4e} м = {r/1000:.2f} км")
            self.final_answer = f"r = {r:.4e} м ({r/1000:.2f} км)"
        
        elif self.task_type == "gravitational_force":
            F = self.G * self.M * self.m / self.r**2
            step1 = templates.get("gravity_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"F = GMm/r² = {self.G:.4e} × {self.M:.4e} × {self.m} / ({self.r:.4e})²")
            self.solution_steps.append(f"F = {F:.4f} Н")
            self.final_answer = f"F = {F:.4f} Н"
        
        elif self.task_type == "schwarzschild":
            r_s = 2 * self.G * self.M / self.c**2
            step1 = templates.get("schwarzschild_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"r_s = 2GM/c² = 2 × {self.G:.4e} × {self.M:.4e} / ({self.c:.4e})²")
            self.solution_steps.append(f"r_s = {r_s:.4e} м")
            self.final_answer = f"r_s = {r_s:.4e} м"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "astrophysics"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
