# re_rl/tasks/physics/mechanics/inclined_plane_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS


class InclinedPlaneTask(BaseMathTask):
    """
    Задачи на движение по наклонной плоскости.
    
    Типы задач:
    - acceleration: ускорение при скольжении
    - min_angle: минимальный угол начала скольжения
    - velocity_at_bottom: скорость в конце спуска
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"angle_range": (20, 40), "mu_range": (0.1, 0.2)},
        3: {"angle_range": (15, 50), "mu_range": (0.1, 0.3)},
        5: {"angle_range": (10, 60), "mu_range": (0.1, 0.4)},
        7: {"angle_range": (10, 70), "mu_range": (0.1, 0.5)},
        10: {"angle_range": (5, 80), "mu_range": (0.1, 0.6)},
    }
    
    TASK_TYPES = ["acceleration", "min_angle", "velocity_at_bottom"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        angle: float = None,
        mu: float = None,
        mass: float = None,
        length: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            angle_range = preset.get("angle_range", (15, 50))
            mu_range = preset.get("mu_range", (0.1, 0.3))
        else:
            angle_range = (15, 50)
            mu_range = (0.1, 0.3)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        self.angle = angle or round(random.uniform(*angle_range), 1)
        self.mu = mu or round(random.uniform(*mu_range), 2)
        self.mass = mass or round(random.uniform(1, 20), 1)
        self.length = length or round(random.uniform(2, 20), 1)
        
        self.g = PHYSICS_CONSTANTS["g"]["value"]
        
        # Вычисляем
        self._calculate()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _calculate(self):
        """Вычисляет параметры движения."""
        angle_rad = math.radians(self.angle)
        
        # Ускорение: a = g(sin(α) - μ·cos(α))
        self.acceleration = self.g * (math.sin(angle_rad) - self.mu * math.cos(angle_rad))
        
        # Минимальный угол: tan(α) = μ
        self.min_angle = math.degrees(math.atan(self.mu))
        
        # Скорость внизу: v = √(2aL)
        if self.acceleration > 0:
            self.velocity_at_bottom = math.sqrt(2 * self.acceleration * self.length)
        else:
            self.velocity_at_bottom = 0

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["inclined_plane"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "acceleration":
            problem_text += templates["problem"]["acceleration"][self.language].format(
                m=self.mass,
                angle=self.angle,
                mu=self.mu
            )
        elif self.task_type == "min_angle":
            problem_text += templates["problem"]["min_angle"][self.language].format(
                mu=self.mu
            )
        else:  # velocity_at_bottom
            problem_text += templates["problem"]["velocity_at_bottom"][self.language].format(
                L=self.length,
                angle=self.angle,
                mu=self.mu
            )
        
        return problem_text

    def solve(self):
        self.solution_steps = []
        
        if self.task_type == "acceleration":
            if self.reasoning_mode:
                self.add_given({"m": self.mass, "α": self.angle, "μ": self.mu}, {"m": "кг", "α": "°", "μ": ""})
                self.add_find("a", "ускорение" if self.language == "ru" else "acceleration")
                self.add_analysis("Силы на тело: mg·sin(α) вниз по склону, μmg·cos(α) — сила трения против движения." if self.language == "ru" else "Forces: mg·sin(α) down the slope, μmg·cos(α) — friction opposing motion.")
            self.add_formula("a = g(sin(α) - μ·cos(α))")
            self.add_substitution(f"a = {self.g}(sin({self.angle}°) - {self.mu}·cos({self.angle}°))")
            self.add_calculation(f"{self.g}×({round(math.sin(math.radians(self.angle)), 4)} - {self.mu}×{round(math.cos(math.radians(self.angle)), 4)})", round(self.acceleration, 3), "м/с²")
            self.final_answer = f"a = {round(self.acceleration, 3)} м/с²"
            
        elif self.task_type == "min_angle":
            if self.reasoning_mode:
                self.add_given({"μ": self.mu}, {"μ": ""})
                self.add_find("α_min", "минимальный угол скольжения" if self.language == "ru" else "minimum sliding angle")
                self.add_analysis("Тело начинает скользить когда mg·sin(α) = μmg·cos(α)" if self.language == "ru" else "Body starts sliding when mg·sin(α) = μmg·cos(α)")
            self.add_formula("tan(α_min) = μ → α_min = arctg(μ)")
            self.add_substitution(f"α_min = arctg({self.mu})")
            self.add_calculation(f"arctg({self.mu})", round(self.min_angle, 2), "°")
            self.final_answer = f"α_min = {round(self.min_angle, 2)}°"
            
        else:  # velocity_at_bottom
            if self.reasoning_mode:
                self.add_given({"L": self.length, "α": self.angle, "μ": self.mu}, {"L": "м", "α": "°", "μ": ""})
                self.add_find("v", "скорость внизу" if self.language == "ru" else "velocity at bottom")
            self.add_formula("a = g(sin(α) - μ·cos(α))")
            self.add_calculation(f"a", round(self.acceleration, 3), "м/с²")
            self.add_formula("v = √(2aL)")
            self.add_substitution(f"v = √(2×{round(self.acceleration, 3)}×{self.length})")
            self.add_calculation(f"√({2*self.acceleration*self.length:.2f})", round(self.velocity_at_bottom, 2), "м/с")
            self.final_answer = f"v = {round(self.velocity_at_bottom, 2)} м/с"

    def get_task_type(self):
        return "inclined_plane"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
