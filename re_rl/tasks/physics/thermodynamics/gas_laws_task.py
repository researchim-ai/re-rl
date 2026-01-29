# re_rl/tasks/physics/thermodynamics/gas_laws_task.py

"""
GasLawsTask — задачи на газовые законы.
"""

import random
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


class GasLawsTask(BaseMathTask):
    """Генератор задач на газовые законы."""
    
    TASK_TYPES = ["ideal_gas", "isothermal", "isobaric", "isochoric", "combined"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_n": 2, "max_T": 400, "max_V": 20, "max_P": 200000},
        2: {"max_n": 5, "max_T": 500, "max_V": 50, "max_P": 500000},
        3: {"max_n": 10, "max_T": 600, "max_V": 100, "max_P": 1000000},
        4: {"max_n": 10, "max_T": 800, "max_V": 200, "max_P": 2000000},
        5: {"max_n": 20, "max_T": 1000, "max_V": 500, "max_P": 5000000},
        6: {"max_n": 50, "max_T": 1000, "max_V": 500, "max_P": 5000000},
        7: {"max_n": 50, "max_T": 1500, "max_V": 1000, "max_P": 10000000},
        8: {"max_n": 100, "max_T": 2000, "max_V": 1000, "max_P": 10000000},
        9: {"max_n": 100, "max_T": 3000, "max_V": 2000, "max_P": 20000000},
        10: {"max_n": 200, "max_T": 5000, "max_V": 5000, "max_P": 50000000},
    }
    
    def __init__(
        self,
        task_type: str = "ideal_gas",
        n: float = None,
        T: float = None,
        T1: float = None,
        T2: float = None,
        V: float = None,
        V1: float = None,
        V2: float = None,
        P1: float = None,
        P2: float = None,
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
        self.R = get_constant("R")
        
        preset = self._interpolate_difficulty(difficulty)
        max_n = preset.get("max_n", 20)
        max_T = preset.get("max_T", 1000)
        max_V = preset.get("max_V", 500)
        max_P = preset.get("max_P", 5000000)
        
        self.n = n if n is not None else round(random.uniform(0.5, max_n), 2)
        self.T = T if T is not None else random.randint(250, max_T)
        self.T1 = T1 if T1 is not None else random.randint(250, max_T // 2)
        self.T2 = T2 if T2 is not None else random.randint(max_T // 2, max_T)
        self.V = V if V is not None else random.randint(1, max_V)
        self.V1 = V1 if V1 is not None else random.randint(1, max_V // 2)
        self.V2 = V2 if V2 is not None else random.randint(max_V // 2, max_V)
        self.P1 = P1 if P1 is not None else random.randint(50000, max_P)
        self.P2 = P2  # Будет вычислено
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("gas_laws", {}).get("problem", {})
        
        if self.task_type == "ideal_gas":
            template = templates.get("ideal_gas", {}).get(self.language, "")
            return template.format(n=self.n, T=self.T, V=self.V)
        elif self.task_type == "isothermal":
            template = templates.get("isothermal", {}).get(self.language, "")
            return template.format(P1=self.P1, V1=self.V1, V2=self.V2)
        elif self.task_type == "isobaric":
            template = templates.get("isobaric", {}).get(self.language, "")
            return template.format(T1=self.T1, V1=self.V1, T2=self.T2)
        elif self.task_type == "isochoric":
            template = templates.get("isochoric", {}).get(self.language, "")
            return template.format(T1=self.T1, P1=self.P1, T2=self.T2)
        elif self.task_type == "combined":
            template = templates.get("combined", {}).get(self.language, "")
            return template.format(P1=self.P1, V1=self.V1, T1=self.T1, V2=self.V2, T2=self.T2)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("gas_laws", {}).get("steps", {})
        
        if self.task_type == "ideal_gas":
            # PV = nRT => P = nRT/V
            V_m3 = self.V / 1000  # л -> м³
            P = self.n * self.R * self.T / V_m3
            step1 = templates.get("ideal_gas_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"P = nRT/V = {self.n} × {self.R} × {self.T} / {V_m3}")
            self.solution_steps.append(f"P = {P:.4f} Па = {P/1000:.4f} кПа")
            self.final_answer = f"{P:.4f} Па"
        
        elif self.task_type == "isothermal":
            # P1V1 = P2V2 => P2 = P1V1/V2
            P2 = self.P1 * self.V1 / self.V2
            step1 = templates.get("boyle_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"P₂ = P₁V₁/V₂ = {self.P1} × {self.V1} / {self.V2} = {P2:.4f} Па")
            self.final_answer = f"{P2:.4f} Па"
        
        elif self.task_type == "isobaric":
            # V1/T1 = V2/T2 => V2 = V1*T2/T1
            V2 = self.V1 * self.T2 / self.T1
            step1 = templates.get("charles_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"V₂ = V₁T₂/T₁ = {self.V1} × {self.T2} / {self.T1} = {V2:.4f} л")
            self.final_answer = f"{V2:.4f} л"
        
        elif self.task_type == "isochoric":
            # P1/T1 = P2/T2 => P2 = P1*T2/T1
            P2 = self.P1 * self.T2 / self.T1
            step1 = templates.get("gay_lussac_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"P₂ = P₁T₂/T₁ = {self.P1} × {self.T2} / {self.T1} = {P2:.4f} Па")
            self.final_answer = f"{P2:.4f} Па"
        
        elif self.task_type == "combined":
            # P1V1/T1 = P2V2/T2 => P2 = P1V1T2/(V2T1)
            P2 = self.P1 * self.V1 * self.T2 / (self.V2 * self.T1)
            step1 = templates.get("combined_law", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"P₂ = P₁V₁T₂/(V₂T₁) = {self.P1} × {self.V1} × {self.T2} / ({self.V2} × {self.T1}) = {P2:.4f} Па"
            )
            self.final_answer = f"{P2:.4f} Па"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "gas_laws"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
