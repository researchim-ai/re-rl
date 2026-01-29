# re_rl/tasks/physics/waves/waves_task.py

"""
WavesTask — задачи на волны.
"""

import random
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.units import format_with_units


class WavesTask(BaseMathTask):
    """Генератор задач на волны."""
    
    TASK_TYPES = ["wavelength", "frequency", "period", "sound_speed", "doppler"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_f": 1000, "max_v": 350, "max_lambda": 10},
        2: {"max_f": 5000, "max_v": 500, "max_lambda": 50},
        3: {"max_f": 10000, "max_v": 1000, "max_lambda": 100},
        4: {"max_f": 20000, "max_v": 2000, "max_lambda": 200},
        5: {"max_f": 50000, "max_v": 5000, "max_lambda": 500},
        6: {"max_f": 100000, "max_v": 10000, "max_lambda": 1000},
        7: {"max_f": 500000, "max_v": 50000, "max_lambda": 5000},
        8: {"max_f": 1000000, "max_v": 100000, "max_lambda": 10000},
        9: {"max_f": 10000000, "max_v": 1000000, "max_lambda": 100000},
        10: {"max_f": 100000000, "max_v": 299792458, "max_lambda": 1000000},
    }
    
    def __init__(
        self,
        task_type: str = "wavelength",
        f: float = None,
        f0: float = None,
        v: float = None,
        v_s: float = None,
        lambda_: float = None,
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
        max_f = preset.get("max_f", 50000)
        max_v = preset.get("max_v", 5000)
        max_lambda = preset.get("max_lambda", 500)
        
        self.f = f if f is not None else random.randint(100, max_f)
        self.f0 = f0 if f0 is not None else random.randint(100, max_f)
        self.v = v if v is not None else random.randint(50, min(max_v, 500))  # Обычно скорость звука
        self.v_s = v_s if v_s is not None else random.randint(10, min(self.v - 10, 100))  # Скорость источника < v
        self.lambda_ = lambda_ if lambda_ is not None else round(random.uniform(0.01, max_lambda), 4)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("waves", {}).get("problem", {})
        
        if self.task_type == "wavelength":
            template = templates.get("wavelength", {}).get(self.language, "")
            return template.format(f=self.f, v=self.v)
        elif self.task_type == "frequency":
            template = templates.get("frequency", {}).get(self.language, "")
            return template.format(lambda_=self.lambda_, v=self.v)
        elif self.task_type == "period":
            template = templates.get("period", {}).get(self.language, "")
            return template.format(f=self.f)
        elif self.task_type == "sound_speed":
            template = templates.get("sound_speed", {}).get(self.language, "")
            return template.format(f=self.f, lambda_=self.lambda_)
        elif self.task_type == "doppler":
            template = templates.get("doppler", {}).get(self.language, "")
            return template.format(f0=self.f0, v_s=self.v_s, v=self.v)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("waves", {}).get("steps", {})
        
        if self.task_type == "wavelength":
            # λ = v/f
            wavelength = self.v / self.f
            step1 = templates.get("wave_equation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"λ = v/f = {self.v}/{self.f} = {wavelength:.4f} м")
            self.final_answer = format_with_units(wavelength, "m", self.language)
        
        elif self.task_type == "frequency":
            # f = v/λ
            f = self.v / self.lambda_
            step1 = templates.get("wave_equation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"f = v/λ = {self.v}/{self.lambda_} = {f:.4f} Гц")
            self.final_answer = f"{f:.4f} Гц"
        
        elif self.task_type == "period":
            # T = 1/f
            T = 1 / self.f
            step1 = templates.get("period_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"T = 1/f = 1/{self.f} = {T:.6f} с")
            self.final_answer = f"{T:.6f} с"
        
        elif self.task_type == "sound_speed":
            # v = λf
            v = self.lambda_ * self.f
            step1 = templates.get("wave_equation", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"v = λf = {self.lambda_} × {self.f} = {v:.4f} м/с")
            self.final_answer = format_with_units(v, "m/s", self.language)
        
        elif self.task_type == "doppler":
            # f' = f0 * v / (v - v_s) (источник приближается)
            f_perceived = self.f0 * self.v / (self.v - self.v_s)
            step1 = templates.get("doppler_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(
                f"f' = f₀ × v/(v - v_s) = {self.f0} × {self.v}/({self.v} - {self.v_s})"
            )
            self.solution_steps.append(f"f' = {f_perceived:.4f} Гц")
            self.final_answer = f"{f_perceived:.4f} Гц"
        
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def get_task_type(self) -> str:
        return "waves"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty)
