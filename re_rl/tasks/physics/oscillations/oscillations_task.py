# re_rl/tasks/physics/oscillations/oscillations_task.py

"""
OscillationsTask — задачи на колебания.

Типы задач:
- harmonic: гармонические колебания
- pendulum: математический маятник
- spring: пружинный маятник
- lc_circuit: LC-контур
- damped: затухающие колебания
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant


class OscillationsTask(BaseMathTask):
    """Генератор задач на колебания."""
    
    TASK_TYPES = [
        "harmonic", "pendulum", "spring", "lc_circuit", "resonance"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_A": 0.1, "max_omega": 10, "max_L": 1, "max_k": 100},
        2: {"max_A": 0.2, "max_omega": 20, "max_L": 2, "max_k": 200},
        3: {"max_A": 0.5, "max_omega": 50, "max_L": 5, "max_k": 500},
        4: {"max_A": 1.0, "max_omega": 100, "max_L": 10, "max_k": 1000},
        5: {"max_A": 2.0, "max_omega": 200, "max_L": 20, "max_k": 2000},
        6: {"max_A": 5.0, "max_omega": 500, "max_L": 50, "max_k": 5000},
        7: {"max_A": 10.0, "max_omega": 1000, "max_L": 100, "max_k": 10000},
        8: {"max_A": 20.0, "max_omega": 2000, "max_L": 200, "max_k": 20000},
        9: {"max_A": 50.0, "max_omega": 5000, "max_L": 500, "max_k": 50000},
        10: {"max_A": 100.0, "max_omega": 10000, "max_L": 1000, "max_k": 100000},
    }
    
    def __init__(
        self,
        task_type: str = "pendulum",
        A: float = None,
        omega: float = None,
        phi: float = None,
        L: float = None,
        m: float = None,
        k: float = None,
        C: float = None,
        L_ind: float = None,
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
        
        self.g = get_constant("g")
        
        preset = self._interpolate_difficulty(difficulty)
        
        self.A = A if A is not None else round(random.uniform(0.01, preset["max_A"]), 3)
        self.omega = omega if omega is not None else round(random.uniform(1, preset["max_omega"]), 2)
        self.phi = phi if phi is not None else random.choice([0, math.pi/6, math.pi/4, math.pi/3, math.pi/2])
        self.L = L if L is not None else round(random.uniform(0.1, min(preset["max_L"], 10)), 2)
        self.m = m if m is not None else round(random.uniform(0.1, 10), 2)
        self.k = k if k is not None else round(random.uniform(10, preset["max_k"]), 1)
        self.C = C if C is not None else random.uniform(1e-9, 1e-6)
        self.L_ind = L_ind if L_ind is not None else random.uniform(1e-3, 1)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("oscillations", {}).get("problem", {})
        
        if self.task_type == "harmonic":
            template = templates.get("harmonic", {}).get(self.language, "")
            return template.format(A=self.A, omega=self.omega)
        elif self.task_type == "pendulum":
            template = templates.get("pendulum", {}).get(self.language, "")
            return template.format(L=self.L, g=self.g)
        elif self.task_type == "spring":
            template = templates.get("spring", {}).get(self.language, "")
            return template.format(k=self.k, m=self.m)
        elif self.task_type == "lc_circuit":
            template = templates.get("lc_circuit", {}).get(self.language, "")
            return template.format(L=self.L_ind*1000, C=self.C*1e6)  # мГн и мкФ
        elif self.task_type == "resonance":
            template = templates.get("resonance", {}).get(self.language, "")
            return template.format(L=self.L_ind*1000, C=self.C*1e6)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("oscillations", {}).get("steps", {})
        
        if self.task_type == "harmonic":
            T = 2 * math.pi / self.omega
            f = 1 / T
            v_max = self.A * self.omega
            step1 = templates.get("harmonic_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"T = 2π/ω = 2π/{self.omega} = {T:.4f} с")
            self.solution_steps.append(f"f = 1/T = {f:.4f} Гц")
            self.solution_steps.append(f"v_max = Aω = {self.A} × {self.omega} = {v_max:.4f} м/с")
            self.final_answer = f"T = {T:.4f} с, f = {f:.4f} Гц"
        
        elif self.task_type == "pendulum":
            T = 2 * math.pi * math.sqrt(self.L / self.g)
            f = 1 / T
            step1 = templates.get("pendulum_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"T = 2π√(L/g) = 2π√({self.L}/{self.g}) = {T:.4f} с")
            self.solution_steps.append(f"f = 1/T = {f:.4f} Гц")
            self.final_answer = f"T = {T:.4f} с"
        
        elif self.task_type == "spring":
            omega = math.sqrt(self.k / self.m)
            T = 2 * math.pi / omega
            f = 1 / T
            step1 = templates.get("spring_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"ω = √(k/m) = √({self.k}/{self.m}) = {omega:.4f} рад/с")
            self.solution_steps.append(f"T = 2π/ω = {T:.4f} с")
            self.final_answer = f"T = {T:.4f} с, ω = {omega:.4f} рад/с"
        
        elif self.task_type == "lc_circuit":
            omega = 1 / math.sqrt(self.L_ind * self.C)
            T = 2 * math.pi / omega
            f = omega / (2 * math.pi)
            step1 = templates.get("lc_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"ω = 1/√(LC) = 1/√({self.L_ind:.4e} × {self.C:.4e}) = {omega:.4f} рад/с")
            self.solution_steps.append(f"T = 2π/ω = {T:.6f} с")
            self.solution_steps.append(f"f = ω/(2π) = {f:.4f} Гц")
            self.final_answer = f"f = {f:.4f} Гц, T = {T:.6f} с"
        
        elif self.task_type == "resonance":
            f_res = 1 / (2 * math.pi * math.sqrt(self.L_ind * self.C))
            step1 = templates.get("resonance_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"f_рез = 1/(2π√(LC)) = {f_res:.4f} Гц")
            self.final_answer = f"f_рез = {f_res:.4f} Гц"
    
    def get_task_type(self) -> str:
        return "oscillations"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
