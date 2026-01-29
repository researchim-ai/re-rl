# re_rl/tasks/physics/electricity/circuits_task.py

"""
CircuitsTask — задачи на электрические цепи.
"""

import random
from typing import Dict, Any, ClassVar, List
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.units import format_with_units


class CircuitsTask(BaseMathTask):
    """Генератор задач на электрические цепи."""
    
    TASK_TYPES = [
        "ohms_law", "find_current", "find_resistance",
        "series", "parallel", "power_circuit"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_R": 50, "max_U": 12, "max_I": 5, "num_resistors": 2},
        2: {"max_R": 100, "max_U": 24, "max_I": 10, "num_resistors": 2},
        3: {"max_R": 200, "max_U": 50, "max_I": 10, "num_resistors": 3},
        4: {"max_R": 500, "max_U": 100, "max_I": 20, "num_resistors": 3},
        5: {"max_R": 500, "max_U": 220, "max_I": 20, "num_resistors": 3},
        6: {"max_R": 1000, "max_U": 220, "max_I": 50, "num_resistors": 4},
        7: {"max_R": 1000, "max_U": 380, "max_I": 50, "num_resistors": 4},
        8: {"max_R": 2000, "max_U": 380, "max_I": 100, "num_resistors": 5},
        9: {"max_R": 5000, "max_U": 500, "max_I": 100, "num_resistors": 5},
        10: {"max_R": 10000, "max_U": 1000, "max_I": 200, "num_resistors": 6},
    }
    
    def __init__(
        self,
        task_type: str = "ohms_law",
        R: float = None,
        U: float = None,
        I: float = None,
        resistors: List[float] = None,
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
        max_R = preset.get("max_R", 500)
        max_U = preset.get("max_U", 220)
        max_I = preset.get("max_I", 20)
        num_resistors = preset.get("num_resistors", 3)
        
        self.R = R if R is not None else random.randint(10, max_R)
        self.U = U if U is not None else random.randint(5, max_U)
        self.I = I if I is not None else round(random.uniform(0.5, max_I), 2)
        self.resistors = resistors if resistors else [
            random.randint(10, max_R) for _ in range(num_resistors)
        ]
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("circuits", {}).get("problem", {})
        
        if self.task_type == "ohms_law":
            template = templates.get("ohms_law", {}).get(self.language, "")
            return template.format(R=self.R, I=self.I)
        elif self.task_type == "find_current":
            template = templates.get("find_current", {}).get(self.language, "")
            return template.format(R=self.R, U=self.U)
        elif self.task_type == "find_resistance":
            template = templates.get("find_resistance", {}).get(self.language, "")
            return template.format(U=self.U, I=self.I)
        elif self.task_type == "series":
            resistors_str = ", ".join([f"{r} Ом" for r in self.resistors])
            template = templates.get("series", {}).get(self.language, "")
            return template.format(resistors=resistors_str)
        elif self.task_type == "parallel":
            resistors_str = ", ".join([f"{r} Ом" for r in self.resistors])
            template = templates.get("parallel", {}).get(self.language, "")
            return template.format(resistors=resistors_str)
        elif self.task_type == "power_circuit":
            template = templates.get("power_circuit", {}).get(self.language, "")
            return template.format(U=self.U, I=self.I)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("circuits", {}).get("steps", {})
        
        if self.task_type == "ohms_law":
            U = self.I * self.R
            step1 = templates.get("ohms_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"U = {self.I} × {self.R} = {U}")
            self.final_answer = format_with_units(U, "V", self.language)
        
        elif self.task_type == "find_current":
            I = self.U / self.R
            step1 = templates.get("ohms_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"I = U/R = {self.U}/{self.R} = {I:.4f}")
            self.final_answer = f"{I:.4f} А"
        
        elif self.task_type == "find_resistance":
            R = self.U / self.I
            step1 = templates.get("ohms_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"R = U/I = {self.U}/{self.I} = {R:.4f}")
            self.final_answer = format_with_units(R, "Ω", self.language)
        
        elif self.task_type == "series":
            R_total = sum(self.resistors)
            step1 = templates.get("series_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            resistors_str = " + ".join([str(r) for r in self.resistors])
            self.solution_steps.append(f"R = {resistors_str} = {R_total}")
            self.final_answer = format_with_units(R_total, "Ω", self.language)
        
        elif self.task_type == "parallel":
            inv_sum = sum(1/r for r in self.resistors)
            R_total = 1 / inv_sum
            step1 = templates.get("parallel_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            inv_str = " + ".join([f"1/{r}" for r in self.resistors])
            self.solution_steps.append(f"1/R = {inv_str} = {inv_sum:.4f}")
            self.solution_steps.append(f"R = {R_total:.4f}")
            self.final_answer = format_with_units(R_total, "Ω", self.language)
        
        elif self.task_type == "power_circuit":
            P = self.U * self.I
            step1 = templates.get("power_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"P = {self.U} × {self.I} = {P}")
            self.final_answer = format_with_units(P, "W", self.language)
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "circuits"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
