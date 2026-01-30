# re_rl/tasks/physics/thermodynamics/heat_transfer_task.py

"""
HeatTransferTask — задачи на теплопередачу.
"""

import random
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


# Удельные теплоёмкости (Дж/(кг·°C))
SPECIFIC_HEAT = {
    "water": {"c": 4186, "name_ru": "вода", "name_en": "water"},
    "ice": {"c": 2090, "name_ru": "лёд", "name_en": "ice"},
    "aluminum": {"c": 897, "name_ru": "алюминий", "name_en": "aluminum"},
    "iron": {"c": 449, "name_ru": "железо", "name_en": "iron"},
    "copper": {"c": 385, "name_ru": "медь", "name_en": "copper"},
    "lead": {"c": 128, "name_ru": "свинец", "name_en": "lead"},
}

# Удельные теплоты (Дж/кг)
LATENT_HEAT = {
    "ice_melting": {"lambda": 334000, "name_ru": "плавления льда", "name_en": "ice melting"},
    "water_vaporization": {"lambda": 2260000, "name_ru": "парообразования воды", "name_en": "water vaporization"},
}


class HeatTransferTask(BaseMathTask):
    """Генератор задач на теплопередачу."""
    
    TASK_TYPES = ["heat_capacity", "mixing", "phase_change", "efficiency"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 2, "max_dT": 50, "max_Q": 100000},
        2: {"max_m": 5, "max_dT": 80, "max_Q": 500000},
        3: {"max_m": 10, "max_dT": 100, "max_Q": 1000000},
        4: {"max_m": 20, "max_dT": 150, "max_Q": 2000000},
        5: {"max_m": 50, "max_dT": 200, "max_Q": 5000000},
        6: {"max_m": 100, "max_dT": 300, "max_Q": 10000000},
        7: {"max_m": 100, "max_dT": 500, "max_Q": 20000000},
        8: {"max_m": 200, "max_dT": 500, "max_Q": 50000000},
        9: {"max_m": 500, "max_dT": 1000, "max_Q": 100000000},
        10: {"max_m": 1000, "max_dT": 1000, "max_Q": 500000000},
    }
    
    def __init__(
        self,
        task_type: str = "heat_capacity",
        m: float = None,
        m1: float = None,
        m2: float = None,
        T1: float = None,
        T2: float = None,
        substance: str = None,
        Q1: float = None,
        Q2: float = None,
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
        
        preset = self._interpolate_difficulty(difficulty)
        max_m = preset.get("max_m", 50)
        max_dT = preset.get("max_dT", 200)
        max_Q = preset.get("max_Q", 5000000)
        
        self.substance = substance or random.choice(list(SPECIFIC_HEAT.keys()))
        self.c = SPECIFIC_HEAT[self.substance]["c"]
        
        self.m = m if m is not None else round(random.uniform(0.1, max_m), 2)
        self.m1 = m1 if m1 is not None else round(random.uniform(0.1, max_m), 2)
        self.m2 = m2 if m2 is not None else round(random.uniform(0.1, max_m), 2)
        self.T1 = T1 if T1 is not None else random.randint(0, 50)
        self.T2 = T2 if T2 is not None else random.randint(50, min(100, self.T1 + max_dT))
        self.Q1 = Q1 if Q1 is not None else random.randint(10000, max_Q)
        self.Q2 = Q2 if Q2 is not None else random.randint(5000, int(self.Q1 * 0.7))
        self.lambda_ice = LATENT_HEAT["ice_melting"]["lambda"]
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _get_substance_name(self) -> str:
        name_key = "name_ru" if self.language == "ru" else "name_en"
        return SPECIFIC_HEAT[self.substance].get(name_key, self.substance)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("heat_transfer", {}).get("problem", {})
        
        if self.task_type == "heat_capacity":
            template = templates.get("heat_capacity", {}).get(self.language, "")
            return template.format(
                m=self.m,
                substance=self._get_substance_name(),
                T1=self.T1,
                T2=self.T2,
                c=self.c
            )
        elif self.task_type == "mixing":
            template = templates.get("mixing", {}).get(self.language, "")
            return template.format(m1=self.m1, T1=self.T1, m2=self.m2, T2=self.T2)
        elif self.task_type == "phase_change":
            template = templates.get("phase_change", {}).get(self.language, "")
            return template.format(m=self.m, lambda_=self.lambda_ice)
        elif self.task_type == "efficiency":
            template = templates.get("efficiency", {}).get(self.language, "")
            return template.format(Q1=self.Q1, Q2=self.Q2)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("heat_transfer", {}).get("steps", {})
        
        if self.task_type == "heat_capacity":
            dT = self.T2 - self.T1
            Q = self.c * self.m * dT
            step1 = templates.get("heat_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"Q = {self.c} × {self.m} × ({self.T2} - {self.T1})")
            self.solution_steps.append(f"Q = {self.c} × {self.m} × {dT} = {Q:.4f} Дж")
            self.final_answer = f"{Q:.4f} Дж"
        
        elif self.task_type == "mixing":
            # c*m1*(T - T1) = c*m2*(T2 - T) => T = (m1*T1 + m2*T2)/(m1+m2)
            T_final = (self.m1 * self.T1 + self.m2 * self.T2) / (self.m1 + self.m2)
            step1 = templates.get("mixing_equation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"T = (m₁T₁ + m₂T₂)/(m₁+m₂) = ({self.m1}×{self.T1} + {self.m2}×{self.T2})/({self.m1}+{self.m2})"
            )
            self.solution_steps.append(f"T = {T_final:.4f} °C")
            self.final_answer = f"{T_final:.4f} °C"
        
        elif self.task_type == "phase_change":
            Q = self.lambda_ice * self.m
            step1 = templates.get("phase_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"Q = λm = {self.lambda_ice} × {self.m} = {Q:.4f} Дж")
            self.final_answer = f"{Q:.4f} Дж"
        
        elif self.task_type == "efficiency":
            eta = (self.Q1 - self.Q2) / self.Q1 * 100
            step1 = templates.get("efficiency_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"η = (Q₁ - Q₂)/Q₁ = ({self.Q1} - {self.Q2})/{self.Q1}")
            self.solution_steps.append(f"η = {eta:.2f}%")
            self.final_answer = f"{eta:.2f}%"
        
        # НЕ обрезаем шаги — в reasoning_mode нужны все шаги
    
    def get_task_type(self) -> str:
        return "heat_transfer"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
