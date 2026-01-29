# re_rl/tasks/physics/electricity/capacitors_task.py

"""
CapacitorsTask — задачи на конденсаторы.
"""

import random
from typing import Dict, Any, ClassVar, List
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.units import format_with_units


class CapacitorsTask(BaseMathTask):
    """Генератор задач на конденсаторы."""
    
    TASK_TYPES = ["charge", "energy", "series", "parallel"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_C": 100e-6, "max_U": 12, "num_caps": 2},
        2: {"max_C": 100e-6, "max_U": 50, "num_caps": 2},
        3: {"max_C": 500e-6, "max_U": 100, "num_caps": 3},
        4: {"max_C": 1e-3, "max_U": 200, "num_caps": 3},
        5: {"max_C": 1e-3, "max_U": 500, "num_caps": 3},
        6: {"max_C": 5e-3, "max_U": 500, "num_caps": 4},
        7: {"max_C": 5e-3, "max_U": 1000, "num_caps": 4},
        8: {"max_C": 10e-3, "max_U": 1000, "num_caps": 5},
        9: {"max_C": 10e-3, "max_U": 2000, "num_caps": 5},
        10: {"max_C": 50e-3, "max_U": 5000, "num_caps": 6},
    }
    
    def __init__(
        self,
        task_type: str = "charge",
        C: float = None,
        U: float = None,
        capacitors: List[float] = None,
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
        max_C = preset.get("max_C", 1e-3)
        max_U = preset.get("max_U", 500)
        num_caps = preset.get("num_caps", 3)
        
        # Генерируем ёмкости в мкФ
        self.C = C if C is not None else round(random.uniform(1e-6, max_C), 9)
        self.U = U if U is not None else random.randint(5, max_U)
        self.capacitors = capacitors if capacitors else [
            round(random.uniform(1e-6, max_C), 9) for _ in range(num_caps)
        ]
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _format_capacitance(self, C: float) -> str:
        """Форматирует ёмкость."""
        if C >= 1e-3:
            return f"{C*1e3:.4g} мФ"
        elif C >= 1e-6:
            return f"{C*1e6:.4g} мкФ"
        elif C >= 1e-9:
            return f"{C*1e9:.4g} нФ"
        else:
            return f"{C*1e12:.4g} пФ"
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("capacitors", {}).get("problem", {})
        
        if self.task_type == "charge":
            template = templates.get("charge", {}).get(self.language, "")
            return template.format(C=self._format_capacitance(self.C), U=self.U)
        elif self.task_type == "energy":
            template = templates.get("energy", {}).get(self.language, "")
            return template.format(C=self._format_capacitance(self.C), U=self.U)
        elif self.task_type == "series":
            caps_str = ", ".join([self._format_capacitance(c) for c in self.capacitors])
            template = templates.get("series", {}).get(self.language, "")
            return template.format(capacitors=caps_str)
        elif self.task_type == "parallel":
            caps_str = ", ".join([self._format_capacitance(c) for c in self.capacitors])
            template = templates.get("parallel", {}).get(self.language, "")
            return template.format(capacitors=caps_str)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("capacitors", {}).get("steps", {})
        
        if self.task_type == "charge":
            q = self.C * self.U
            step1 = templates.get("charge_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"q = {self.C:.2e} × {self.U} = {q:.4e} Кл")
            self.final_answer = f"{q:.4e} Кл"
        
        elif self.task_type == "energy":
            W = self.C * self.U ** 2 / 2
            step1 = templates.get("energy_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"W = {self.C:.2e} × {self.U}² / 2 = {W:.4e} Дж")
            self.final_answer = f"{W:.4e} Дж"
        
        elif self.task_type == "series":
            inv_sum = sum(1/c for c in self.capacitors)
            C_total = 1 / inv_sum
            step1 = templates.get("series_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"C = {C_total:.4e} Ф = {self._format_capacitance(C_total)}")
            self.final_answer = self._format_capacitance(C_total)
        
        elif self.task_type == "parallel":
            C_total = sum(self.capacitors)
            step1 = templates.get("parallel_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"C = {C_total:.4e} Ф = {self._format_capacitance(C_total)}")
            self.final_answer = self._format_capacitance(C_total)
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "capacitors"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
