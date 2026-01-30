# re_rl/tasks/physics/mechanics/rotational_dynamics_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class RotationalDynamicsTask(BaseMathTask):
    """
    Задачи на вращательное движение.
    
    Типы задач:
    - moment_of_inertia: момент инерции
    - angular_acceleration: угловое ускорение
    - rotational_energy: кинетическая энергия вращения
    - angular_momentum: момент импульса
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"I_range": (0.1, 1), "omega_range": (1, 5)},
        3: {"I_range": (0.5, 5), "omega_range": (2, 10)},
        5: {"I_range": (1, 10), "omega_range": (5, 20)},
        7: {"I_range": (5, 50), "omega_range": (10, 50)},
        10: {"I_range": (10, 100), "omega_range": (20, 100)},
    }
    
    TASK_TYPES = ["moment_of_inertia", "angular_acceleration", "rotational_energy", "angular_momentum"]
    
    # Моменты инерции для разных форм
    SHAPES = {
        "disk": {"formula": "I = MR²/2", "factor": 0.5},
        "sphere": {"formula": "I = 2MR²/5", "factor": 0.4},
        "rod": {"formula": "I = ML²/12", "factor": 1/12},
        "ring": {"formula": "I = MR²", "factor": 1.0},
        "cylinder": {"formula": "I = MR²/2", "factor": 0.5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            I_range = preset.get("I_range", (1, 10))
            omega_range = preset.get("omega_range", (5, 20))
        else:
            I_range = (1, 10)
            omega_range = (5, 20)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Генерируем параметры
        self.I = round(random.uniform(*I_range), 2)
        self.omega = round(random.uniform(*omega_range), 2)
        self.M_torque = round(random.uniform(1, 50), 2)
        self.mass = round(random.uniform(1, 20), 2)
        self.radius = round(random.uniform(0.1, 2), 2)
        self.shape = random.choice(list(self.SHAPES.keys()))
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["rotational_dynamics"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "moment_of_inertia":
            shape_name = templates["shapes"][self.shape][self.language]
            problem_text += templates["problem"]["moment_of_inertia"][self.language].format(
                shape=shape_name,
                m=self.mass,
                param_name="радиусом" if self.language == "ru" else "radius",
                param_value=self.radius,
                axis="центра масс" if self.language == "ru" else "center of mass"
            )
        elif self.task_type == "angular_acceleration":
            problem_text += templates["problem"]["angular_acceleration"][self.language].format(
                I=self.I,
                M=self.M_torque
            )
        elif self.task_type == "rotational_energy":
            problem_text += templates["problem"]["rotational_energy"][self.language].format(
                I=self.I,
                omega=self.omega
            )
        else:  # angular_momentum
            problem_text += templates["problem"]["angular_momentum"][self.language].format(
                I=self.I,
                omega=self.omega
            )
        
        return problem_text

    def solve(self):
        self.solution_steps = []
        
        if self.task_type == "moment_of_inertia":
            factor = self.SHAPES[self.shape]["factor"]
            I_calc = factor * self.mass * self.radius ** 2
            formula = self.SHAPES[self.shape]["formula"]
            if self.reasoning_mode:
                self.add_given({"M": self.mass, "R": self.radius}, {"M": "кг", "R": "м"})
                self.add_find("I", "момент инерции" if self.language == "ru" else "moment of inertia")
            self.add_formula(formula)
            self.add_substitution(f"I = {factor}·{self.mass}·{self.radius}²")
            self.add_calculation(f"{factor}×{self.mass}×{self.radius**2}", round(I_calc, 4), "кг·м²")
            if self.reasoning_mode:
                self.add_dimension_check("[кг]×[м²] = [кг·м²] ✓")
            self.final_answer = f"I = {round(I_calc, 4)} кг·м²"
            
        elif self.task_type == "angular_acceleration":
            epsilon = self.M_torque / self.I
            if self.reasoning_mode:
                self.add_given({"I": self.I, "M": self.M_torque}, {"I": "кг·м²", "M": "Н·м"})
                self.add_find("ε", "угловое ускорение" if self.language == "ru" else "angular acceleration")
                self.add_analysis("Второй закон Ньютона для вращения: M = Iε" if self.language == "ru" else "Newton's second law for rotation: M = Iε")
            self.add_formula("M = Iε → ε = M/I")
            self.add_substitution(f"ε = {self.M_torque} / {self.I}")
            self.add_calculation(f"{self.M_torque}/{self.I}", round(epsilon, 3), "рад/с²")
            self.final_answer = f"ε = {round(epsilon, 3)} рад/с²"
            
        elif self.task_type == "rotational_energy":
            E = 0.5 * self.I * self.omega ** 2
            if self.reasoning_mode:
                self.add_given({"I": self.I, "ω": self.omega}, {"I": "кг·м²", "ω": "рад/с"})
                self.add_find("E", "кинетическая энергия вращения" if self.language == "ru" else "rotational kinetic energy")
            self.add_formula("E = Iω²/2")
            self.add_substitution(f"E = {self.I}·{self.omega}²/2")
            self.add_calculation(f"{self.I}×{self.omega**2}/2", round(E, 2), "Дж")
            if self.reasoning_mode:
                self.add_dimension_check("[кг·м²]×[рад/с]² = [Дж] ✓")
            self.final_answer = f"E = {round(E, 2)} Дж"
            
        else:  # angular_momentum
            L = self.I * self.omega
            if self.reasoning_mode:
                self.add_given({"I": self.I, "ω": self.omega}, {"I": "кг·м²", "ω": "рад/с"})
                self.add_find("L", "момент импульса" if self.language == "ru" else "angular momentum")
            self.add_formula("L = Iω")
            self.add_substitution(f"L = {self.I}·{self.omega}")
            self.add_calculation(f"{self.I}×{self.omega}", round(L, 2), "кг·м²/с")
            self.final_answer = f"L = {round(L, 2)} кг·м²/с"

    def get_task_type(self):
        return "rotational_dynamics"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
