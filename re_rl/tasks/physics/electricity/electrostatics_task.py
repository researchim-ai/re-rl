# re_rl/tasks/physics/electricity/electrostatics_task.py

"""
ElectrostaticsTask — задачи по электростатике.
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.units import format_with_units


class ElectrostaticsTask(BaseMathTask):
    """Генератор задач по электростатике."""
    
    TASK_TYPES = ["coulomb", "electric_field", "potential", "work_in_field"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_q": 1e-6, "max_r": 1, "max_E": 1000},
        2: {"max_q": 1e-6, "max_r": 2, "max_E": 5000},
        3: {"max_q": 5e-6, "max_r": 5, "max_E": 10000},
        4: {"max_q": 1e-5, "max_r": 5, "max_E": 20000},
        5: {"max_q": 1e-5, "max_r": 10, "max_E": 50000},
        6: {"max_q": 5e-5, "max_r": 10, "max_E": 100000},
        7: {"max_q": 1e-4, "max_r": 20, "max_E": 100000},
        8: {"max_q": 1e-4, "max_r": 50, "max_E": 500000},
        9: {"max_q": 5e-4, "max_r": 50, "max_E": 1000000},
        10: {"max_q": 1e-3, "max_r": 100, "max_E": 1000000},
    }
    
    def __init__(
        self,
        task_type: str = "coulomb",
        q1: float = None,
        q2: float = None,
        q: float = None,
        r: float = None,
        E: float = None,
        d: float = None,
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
        self.k = get_constant("k_e")
        
        preset = self._interpolate_difficulty(difficulty)
        max_q = preset.get("max_q", 1e-5)
        max_r = preset.get("max_r", 10)
        max_E = preset.get("max_E", 50000)
        
        # Генерируем заряды в мкКл для удобства
        self.q1 = q1 if q1 is not None else round(random.uniform(1e-9, max_q), 9)
        self.q2 = q2 if q2 is not None else round(random.uniform(1e-9, max_q), 9)
        self.q = q if q is not None else round(random.uniform(1e-9, max_q), 9)
        self.r = r if r is not None else round(random.uniform(0.01, max_r), 2)
        self.E = E if E is not None else random.randint(100, max_E)
        self.d = d if d is not None else round(random.uniform(0.01, max_r), 2)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _format_charge(self, q: float) -> str:
        """Форматирует заряд в удобные единицы."""
        if abs(q) >= 1e-3:
            return f"{q*1e3:.4g} мКл"
        elif abs(q) >= 1e-6:
            return f"{q*1e6:.4g} мкКл"
        elif abs(q) >= 1e-9:
            return f"{q*1e9:.4g} нКл"
        else:
            return f"{q:.4g} Кл"
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("electrostatics", {}).get("problem", {})
        
        if self.task_type == "coulomb":
            template = templates.get("coulomb", {}).get(self.language, "")
            return template.format(
                q1=self._format_charge(self.q1),
                q2=self._format_charge(self.q2),
                r=self.r
            )
        elif self.task_type == "electric_field":
            template = templates.get("electric_field", {}).get(self.language, "")
            return template.format(q=self._format_charge(self.q), r=self.r)
        elif self.task_type == "potential":
            template = templates.get("potential", {}).get(self.language, "")
            return template.format(q=self._format_charge(self.q), r=self.r)
        elif self.task_type == "work_in_field":
            template = templates.get("work_in_field", {}).get(self.language, "")
            return template.format(q=self._format_charge(self.q), E=self.E, d=self.d)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("electrostatics", {}).get("steps", {})
        
        if self.task_type == "coulomb":
            F = self.k * abs(self.q1 * self.q2) / (self.r ** 2)
            step1 = templates.get("coulomb_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"F = 9×10⁹ × |{self.q1:.2e} × {self.q2:.2e}| / {self.r}² = {F:.4e} Н"
            )
            self.final_answer = f"{F:.4e} Н"
        
        elif self.task_type == "electric_field":
            E = self.k * abs(self.q) / (self.r ** 2)
            step1 = templates.get("field_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"E = 9×10⁹ × |{self.q:.2e}| / {self.r}² = {E:.4e} В/м"
            )
            self.final_answer = f"{E:.4e} В/м"
        
        elif self.task_type == "potential":
            phi = self.k * self.q / self.r
            step1 = templates.get("potential_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"φ = 9×10⁹ × {self.q:.2e} / {self.r} = {phi:.4e} В"
            )
            self.final_answer = f"{phi:.4e} В"
        
        elif self.task_type == "work_in_field":
            A = self.q * self.E * self.d
            self.solution_steps.append(f"A = qEd = {self.q:.2e} × {self.E} × {self.d} = {A:.4e} Дж")
            self.final_answer = f"{A:.4e} Дж"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "electrostatics"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
