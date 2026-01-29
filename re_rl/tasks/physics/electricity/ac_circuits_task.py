# re_rl/tasks/physics/electricity/ac_circuits_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ACCircuitsTask(BaseMathTask):
    """
    Задачи на цепи переменного тока.
    
    Типы задач:
    - impedance: импеданс RLC-цепи
    - resonance: резонансная частота
    - power_factor: коэффициент мощности
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"R_range": (10, 100), "simple": True},
        3: {"R_range": (50, 500), "simple": True},
        5: {"R_range": (100, 1000), "simple": False},
        7: {"R_range": (200, 2000), "simple": False},
        10: {"R_range": (500, 5000), "simple": False},
    }
    
    TASK_TYPES = ["impedance", "resonance", "power_factor"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        R: float = None,
        L: float = None,
        C: float = None,
        f: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            R_range = preset.get("R_range", (100, 1000))
        else:
            R_range = (100, 1000)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Генерируем параметры
        self.R = R or round(random.uniform(*R_range), 1)
        self.L = L or round(random.uniform(0.01, 1.0), 3)  # Гн
        self.C = C or round(random.uniform(1, 100), 1)  # мкФ
        self.f = f or round(random.uniform(50, 1000), 1)  # Гц
        
        # Конвертируем C в Ф
        self.C_farads = self.C * 1e-6
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["ac_circuits"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "impedance":
            problem_text += templates["problem"]["impedance"][self.language].format(
                R=self.R,
                L=self.L,
                C=self.C,
                f=self.f
            )
        elif self.task_type == "resonance":
            problem_text += templates["problem"]["resonance"][self.language].format(
                L=self.L,
                C=self.C
            )
        else:  # power_factor
            omega = 2 * math.pi * self.f
            XL = omega * self.L
            XC = 1 / (omega * self.C_farads)
            problem_text += templates["problem"]["power_factor"][self.language].format(
                R=self.R,
                XL=round(XL, 2),
                XC=round(XC, 2)
            )
        
        return problem_text

    def solve(self):
        templates = PROMPT_TEMPLATES["ac_circuits"]
        steps = []
        
        omega = 2 * math.pi * self.f
        XL = omega * self.L
        XC = 1 / (omega * self.C_farads) if self.C_farads > 0 else 0
        
        if self.task_type == "impedance":
            steps.append(templates["steps"]["reactances"][self.language].format(
                XL=round(XL, 2),
                XC=round(XC, 2)
            ))
            steps.append(templates["steps"]["impedance_formula"][self.language])
            Z = math.sqrt(self.R**2 + (XL - XC)**2)
            steps.append(f"Z = √({self.R}² + ({round(XL, 2)} - {round(XC, 2)})²) = {round(Z, 2)} Ом")
            self.result = round(Z, 2)
            answer = f"Z = {self.result} Ом"
            
        elif self.task_type == "resonance":
            steps.append(templates["steps"]["resonance_formula"][self.language])
            f0 = 1 / (2 * math.pi * math.sqrt(self.L * self.C_farads))
            steps.append(f"f₀ = 1/(2π√({self.L}·{self.C}·10⁻⁶)) = {round(f0, 2)} Гц")
            self.result = round(f0, 2)
            answer = f"f₀ = {self.result} Гц"
            
        else:  # power_factor
            Z = math.sqrt(self.R**2 + (XL - XC)**2)
            cos_phi = self.R / Z if Z > 0 else 1
            steps.append(f"Z = √(R² + (X_L - X_C)²) = {round(Z, 2)} Ом")
            steps.append(f"cos(φ) = R/Z = {self.R}/{round(Z, 2)} = {round(cos_phi, 4)}")
            self.result = round(cos_phi, 4)
            answer = f"cos(φ) = {self.result}"
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = templates["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "ac_circuits"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
