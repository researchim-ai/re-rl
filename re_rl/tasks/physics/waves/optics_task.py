# re_rl/tasks/physics/waves/optics_task.py

"""
OpticsTask — задачи по оптике.
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class OpticsTask(BaseMathTask):
    """Генератор задач по оптике."""
    
    TASK_TYPES = ["snell", "critical_angle", "thin_lens", "magnification", "mirror"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_n": 1.5, "max_f": 20, "max_d": 50},
        2: {"max_n": 1.7, "max_f": 30, "max_d": 100},
        3: {"max_n": 2.0, "max_f": 50, "max_d": 150},
        4: {"max_n": 2.2, "max_f": 75, "max_d": 200},
        5: {"max_n": 2.4, "max_f": 100, "max_d": 300},
        6: {"max_n": 2.5, "max_f": 150, "max_d": 400},
        7: {"max_n": 2.7, "max_f": 200, "max_d": 500},
        8: {"max_n": 3.0, "max_f": 300, "max_d": 1000},
        9: {"max_n": 3.5, "max_f": 500, "max_d": 2000},
        10: {"max_n": 4.0, "max_f": 1000, "max_d": 5000},
    }
    
    def __init__(
        self,
        task_type: str = "snell",
        n1: float = None,
        n2: float = None,
        angle1: float = None,
        f: float = None,
        d: float = None,
        d_obj: float = None,
        f_img: float = None,
        R: float = None,
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
        max_n = preset.get("max_n", 2.4)
        max_f = preset.get("max_f", 100)
        max_d = preset.get("max_d", 300)
        
        # Показатели преломления
        self.n1 = n1 if n1 is not None else round(random.uniform(1.0, max_n), 2)
        self.n2 = n2 if n2 is not None else round(random.uniform(1.0, max_n), 2)
        
        # Для закона Снелла нужно n1 > n2 для критического угла
        if self.task_type == "critical_angle" and self.n1 <= self.n2:
            self.n1, self.n2 = max(self.n1, self.n2), min(self.n1, self.n2)
        
        self.angle1 = angle1 if angle1 is not None else random.randint(10, 60)
        self.f = f if f is not None else random.randint(5, max_f)
        self.d = d if d is not None else random.randint(int(self.f * 1.5), max_d)  # d > f для реального изображения
        self.d_obj = d_obj if d_obj is not None else random.randint(int(self.f * 1.5), max_d)
        self.f_img = f_img if f_img is not None else random.randint(int(self.f * 1.5), max_d)
        self.R = R if R is not None else random.randint(10, max_f * 2)
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _create_problem_description(self) -> str:
        templates = PROMPT_TEMPLATES.get("optics", {}).get("problem", {})
        
        if self.task_type == "snell":
            template = templates.get("snell", {}).get(self.language, "")
            return template.format(n1=self.n1, n2=self.n2, angle1=self.angle1)
        elif self.task_type == "critical_angle":
            template = templates.get("critical_angle", {}).get(self.language, "")
            return template.format(n1=self.n1, n2=self.n2)
        elif self.task_type == "thin_lens":
            template = templates.get("thin_lens", {}).get(self.language, "")
            return template.format(d=self.d, f=self.f)
        elif self.task_type == "magnification":
            template = templates.get("magnification", {}).get(self.language, "")
            return template.format(f_img=self.f_img, d_obj=self.d_obj)
        elif self.task_type == "mirror":
            template = templates.get("mirror", {}).get(self.language, "")
            return template.format(d=self.d, R=self.R)
        return ""
    
    def solve(self):
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("optics", {}).get("steps", {})
        
        if self.task_type == "snell":
            # n1*sin(θ1) = n2*sin(θ2) => sin(θ2) = n1*sin(θ1)/n2
            sin_theta2 = self.n1 * math.sin(math.radians(self.angle1)) / self.n2
            if sin_theta2 <= 1:
                theta2 = math.degrees(math.asin(sin_theta2))
                step1 = templates.get("snell_law", {}).get(self.language, "")
                self.solution_steps.append(step1)
                self.solution_steps.append(
                    f"sin(θ₂) = n₁sin(θ₁)/n₂ = {self.n1}×sin({self.angle1}°)/{self.n2} = {sin_theta2:.4f}"
                )
                self.solution_steps.append(f"θ₂ = arcsin({sin_theta2:.4f}) = {theta2:.2f}°")
                self.final_answer = f"{theta2:.2f}°"
            else:
                self.final_answer = "Полное внутреннее отражение"
        
        elif self.task_type == "critical_angle":
            # sin(θc) = n2/n1
            if self.n1 > self.n2:
                sin_critical = self.n2 / self.n1
                theta_c = math.degrees(math.asin(sin_critical))
                self.solution_steps.append(f"sin(θc) = n₂/n₁ = {self.n2}/{self.n1} = {sin_critical:.4f}")
                self.solution_steps.append(f"θc = arcsin({sin_critical:.4f}) = {theta_c:.2f}°")
                self.final_answer = f"{theta_c:.2f}°"
            else:
                self.final_answer = "Полное внутреннее отражение невозможно (n₁ ≤ n₂)"
        
        elif self.task_type == "thin_lens":
            # 1/f = 1/d + 1/f' => f' = d*f/(d-f)
            if self.d != self.f:
                f_prime = self.d * self.f / (self.d - self.f)
                step1 = templates.get("lens_formula", {}).get(self.language, "")
                self.solution_steps.append(step1)
                self.solution_steps.append(f"f' = d·F/(d-F) = {self.d}×{self.f}/({self.d}-{self.f}) = {f_prime:.2f} см")
                self.final_answer = f"{f_prime:.2f} см"
            else:
                self.final_answer = "Изображение на бесконечности"
        
        elif self.task_type == "magnification":
            # Г = f'/d
            magnification = abs(self.f_img / self.d_obj)
            step1 = templates.get("magnification_formula", {}).get(self.language, "")
            self.solution_steps.append(step1)
            self.solution_steps.append(f"Г = |f'/d| = |{self.f_img}/{self.d_obj}| = {magnification:.4f}")
            self.final_answer = f"{magnification:.4f}"
        
        elif self.task_type == "mirror":
            # 1/d + 1/f' = 2/R => f' = d*R/(2d - R)
            f_mirror = self.R / 2  # Фокусное расстояние
            if 2 * self.d != self.R:
                f_prime = self.d * self.R / (2 * self.d - self.R)
                step1 = templates.get("mirror_formula", {}).get(self.language, "")
                self.solution_steps.append(step1)
                self.solution_steps.append(f"F = R/2 = {self.R}/2 = {f_mirror} см")
                self.solution_steps.append(f"f' = d·R/(2d-R) = {self.d}×{self.R}/(2×{self.d}-{self.R}) = {f_prime:.2f} см")
                self.final_answer = f"{f_prime:.2f} см"
            else:
                self.final_answer = "Изображение на бесконечности"
        
    
    def get_task_type(self) -> str:
        return "optics"
    
    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                            detail_level: int = 3, difficulty: int = 5, reasoning_mode: bool = False):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(task_type=task_type, language=language,
                  detail_level=detail_level, difficulty=difficulty, reasoning_mode=reasoning_mode)
