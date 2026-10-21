from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/mechanics/rotational_dynamics_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


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
    
    TASK_TYPES = [texts.literal('literals.s0'), "angular_acceleration", "rotational_energy", "angular_momentum"]
    
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
        
        if self.task_type == texts.t('s1', self.language):
            shape_name = templates["shapes"][self.shape][self.language]
            problem_text += templates["problem"][texts.t('s17', self.language)][self.language].format(
                shape=shape_name,
                m=self.mass,
                param_name=get_template(PROMPT_TEMPLATES["inline"], texts.t('s10', self.language), self.language, augment=False),
                param_value=self.radius,
                axis=get_template(PROMPT_TEMPLATES["inline"], texts.t('s11', self.language), self.language, augment=False)
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
        
        if self.task_type == texts.t('s2', self.language):
            factor = self.SHAPES[self.shape]["factor"]
            I_calc = factor * self.mass * self.radius ** 2
            formula = self.SHAPES[self.shape]["formula"]
            if self.reasoning_mode:
                self.add_given({"M": self.mass, "R": self.radius}, {"M": texts.t('s12', self.language), "R": texts.t('s13', self.language)})
                self.add_find("I", get_template(PROMPT_TEMPLATES["inline"], texts.t('s14', self.language), self.language, augment=False))
            self.add_formula(formula)
            self.add_substitution(f"I = {factor}·{self.mass}·{self.radius}²")
            self.add_calculation(f"{factor}×{self.mass}×{self.radius**2}", round(I_calc, 4), texts.t('s4', self.language))
            if self.reasoning_mode:
                self.add_dimension_check(texts.literal('literals.s6'))
            self.final_answer = texts.t('s3', self.language, v0=round(I_calc, 4))
            
        elif self.task_type == "angular_acceleration":
            epsilon = self.M_torque / self.I
            if self.reasoning_mode:
                self.add_given({"I": self.I, "M": self.M_torque}, {"I": texts.t('s18', self.language), "M": texts.t('s19', self.language)})
                self.add_find("ε", get_template(PROMPT_TEMPLATES["inline"], texts.t('s20', self.language), self.language, augment=False))
                self.add_analysis(get_template(PROMPT_TEMPLATES["inline"], texts.t('s21', self.language), self.language, augment=False))
            self.add_formula("M = Iε → ε = M/I")
            self.add_substitution(f"ε = {self.M_torque} / {self.I}")
            self.add_calculation(f"{self.M_torque}/{self.I}", round(epsilon, 3), texts.t('s7', self.language))
            self.final_answer = texts.t('s5', self.language, v0=round(epsilon, 3))
            
        elif self.task_type == "rotational_energy":
            E = 0.5 * self.I * self.omega ** 2
            if self.reasoning_mode:
                self.add_given({"I": self.I, "ω": self.omega}, {"I": texts.t('s23', self.language), "ω": texts.t('s24', self.language)})
                self.add_find("E", get_template(PROMPT_TEMPLATES["inline"], texts.t('s25', self.language), self.language, augment=False))
            self.add_formula("E = Iω²/2")
            self.add_substitution(f"E = {self.I}·{self.omega}²/2")
            self.add_calculation(f"{self.I}×{self.omega**2}/2", round(E, 2), texts.t('s15', self.language))
            if self.reasoning_mode:
                self.add_dimension_check(texts.literal('literals.s22'))
            self.final_answer = texts.t('s8', self.language, v0=round(E, 2))
            
        else:  # angular_momentum
            L = self.I * self.omega
            if self.reasoning_mode:
                self.add_given({"I": self.I, "ω": self.omega}, {"I": texts.t('s26', self.language), "ω": texts.t('s27', self.language)})
                self.add_find("L", get_template(PROMPT_TEMPLATES["inline"], texts.t('s28', self.language), self.language, augment=False))
            self.add_formula("L = Iω")
            self.add_substitution(f"L = {self.I}·{self.omega}")
            self.add_calculation(f"{self.I}×{self.omega}", round(L, 2), texts.t('s16', self.language))
            self.final_answer = texts.t('s9', self.language, v0=round(L, 2))

    def get_task_type(self):
        return "rotational_dynamics"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
