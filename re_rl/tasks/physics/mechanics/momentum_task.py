# re_rl/tasks/physics/mechanics/momentum_task.py

"""
MomentumTask — задачи на импульс и столкновения.
"""

import random
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.units import format_with_units


class MomentumTask(BaseMathTask):
    """Генератор задач на импульс."""
    
    TASK_TYPES = ["momentum", "impulse", "inelastic_collision", "elastic_collision"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 10, "max_v": 10, "max_F": 50, "max_t": 5},
        2: {"max_m": 20, "max_v": 20, "max_F": 100, "max_t": 10},
        3: {"max_m": 30, "max_v": 30, "max_F": 200, "max_t": 10},
        4: {"max_m": 50, "max_v": 50, "max_F": 300, "max_t": 15},
        5: {"max_m": 50, "max_v": 50, "max_F": 500, "max_t": 15},
        6: {"max_m": 100, "max_v": 100, "max_F": 500, "max_t": 20},
        7: {"max_m": 100, "max_v": 100, "max_F": 1000, "max_t": 20},
        8: {"max_m": 200, "max_v": 150, "max_F": 1000, "max_t": 30},
        9: {"max_m": 200, "max_v": 200, "max_F": 2000, "max_t": 30},
        10: {"max_m": 500, "max_v": 300, "max_F": 5000, "max_t": 60},
    }
    
    def __init__(
        self,
        task_type: str = "momentum",
        m: float = None,
        m1: float = None,
        m2: float = None,
        v: float = None,
        v1: float = None,
        F: float = None,
        t: float = None,
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
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.m = m if m is not None else random.randint(1, preset["max_m"])
        self.m1 = m1 if m1 is not None else random.randint(1, preset["max_m"])
        self.m2 = m2 if m2 is not None else random.randint(1, preset["max_m"])
        self.v = v if v is not None else random.randint(5, preset["max_v"])
        self.v1 = v1 if v1 is not None else random.randint(5, preset["max_v"])
        self.F = F if F is not None else random.randint(10, preset["max_F"])
        self.t = t if t is not None else random.randint(1, preset["max_t"])
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("momentum", {}).get("problem", {})
        
        if self.task_type == "momentum":
            template = templates.get("momentum", {}).get(self.language, "")
            return template.format(m=self.m, v=self.v)
        elif self.task_type == "impulse":
            template = templates.get("impulse", {}).get(self.language, "")
            return template.format(F=self.F, t=self.t)
        elif self.task_type == "inelastic_collision":
            template = templates.get("inelastic_collision", {}).get(self.language, "")
            return template.format(m1=self.m1, v1=self.v1, m2=self.m2)
        elif self.task_type == "elastic_collision":
            template = templates.get("elastic_collision", {}).get(self.language, "")
            return template.format(m1=self.m1, v1=self.v1, m2=self.m2)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("momentum", {}).get("steps", {})
        
        if self.task_type == "momentum":
            p = self.m * self.v
            step1 = templates.get("momentum_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"p = {self.m} × {self.v} = {p}")
            self.final_answer = format_with_units(p, "kg", self.language) + "·м/с"
        
        elif self.task_type == "impulse":
            J = self.F * self.t
            self.solution_steps.append(f"J = F·t = {self.F} × {self.t} = {J}")
            self.final_answer = f"{J} Н·с"
        
        elif self.task_type == "inelastic_collision":
            # m1*v1 = (m1+m2)*v'
            v_final = self.m1 * self.v1 / (self.m1 + self.m2)
            step1 = templates.get("conservation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"v' = m₁v₁/(m₁+m₂) = {self.m1}×{self.v1}/({self.m1}+{self.m2}) = {v_final:.4f}"
            )
            self.final_answer = format_with_units(v_final, "m/s", self.language)
        
        elif self.task_type == "elastic_collision":
            # Для упругого столкновения с неподвижным телом:
            # v1' = (m1-m2)/(m1+m2) * v1
            # v2' = 2*m1/(m1+m2) * v1
            v1_final = (self.m1 - self.m2) / (self.m1 + self.m2) * self.v1
            v2_final = 2 * self.m1 / (self.m1 + self.m2) * self.v1
            
            step1 = templates.get("conservation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"v₁' = (m₁-m₂)/(m₁+m₂)·v₁ = ({self.m1}-{self.m2})/({self.m1}+{self.m2})×{self.v1} = {v1_final:.4f}"
            )
            self.solution_steps.append(
                f"v₂' = 2m₁/(m₁+m₂)·v₁ = 2×{self.m1}/({self.m1}+{self.m2})×{self.v1} = {v2_final:.4f}"
            )
            self.final_answer = f"v₁' = {v1_final:.4f} м/с, v₂' = {v2_final:.4f} м/с"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "momentum"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
