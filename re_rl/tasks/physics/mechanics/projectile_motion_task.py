# re_rl/tasks/physics/mechanics/projectile_motion_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS


class ProjectileMotionTask(BaseMathTask):
    """
    Задачи на движение тела, брошенного под углом к горизонту.
    
    Типы задач:
    - range: дальность полёта
    - max_height: максимальная высота
    - flight_time: время полёта
    - velocity_at_height: скорость на заданной высоте
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v0_range": (5, 15), "angle_simple": True},
        2: {"v0_range": (10, 20), "angle_simple": True},
        3: {"v0_range": (10, 30), "angle_simple": False},
        4: {"v0_range": (15, 40), "angle_simple": False},
        5: {"v0_range": (20, 50), "angle_simple": False},
        6: {"v0_range": (20, 60), "angle_simple": False},
        7: {"v0_range": (30, 80), "angle_simple": False},
        8: {"v0_range": (40, 100), "angle_simple": False},
        9: {"v0_range": (50, 150), "angle_simple": False},
        10: {"v0_range": (100, 300), "angle_simple": False},
    }
    
    TASK_TYPES = ["range", "max_height", "flight_time", "velocity_at_height"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        v0: float = None,
        angle: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            v0_range = preset.get("v0_range", (10, 50))
            angle_simple = preset.get("angle_simple", False)
        else:
            v0_range = (10, 50)
            angle_simple = False
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        self.v0 = v0 or random.uniform(*v0_range)
        
        if angle is not None:
            self.angle = angle
        elif angle_simple:
            self.angle = random.choice([30, 45, 60])
        else:
            self.angle = random.uniform(15, 75)
        
        self.g = PHYSICS_CONSTANTS["g"]["value"]
        
        # Вычисляем все величины
        self._calculate()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _calculate(self):
        """Вычисляет все параметры движения."""
        angle_rad = math.radians(self.angle)
        
        self.vx = self.v0 * math.cos(angle_rad)
        self.vy = self.v0 * math.sin(angle_rad)
        
        # Дальность полёта
        self.range_val = (self.v0 ** 2 * math.sin(2 * angle_rad)) / self.g
        
        # Максимальная высота
        self.max_height = (self.v0 ** 2 * math.sin(angle_rad) ** 2) / (2 * self.g)
        
        # Время полёта
        self.flight_time = (2 * self.v0 * math.sin(angle_rad)) / self.g

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["projectile_motion"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "range":
            problem_text += templates["problem"]["range"][self.language].format(
                angle=round(self.angle, 1),
                v0=round(self.v0, 1)
            )
        elif self.task_type == "max_height":
            problem_text += templates["problem"]["max_height"][self.language].format(
                angle=round(self.angle, 1),
                v0=round(self.v0, 1)
            )
        elif self.task_type == "flight_time":
            problem_text += templates["problem"]["flight_time"][self.language].format(
                angle=round(self.angle, 1),
                v0=round(self.v0, 1)
            )
        else:  # velocity_at_height
            h = round(self.max_height * random.uniform(0.3, 0.8), 2)
            self.height_query = h
            problem_text += templates["problem"]["velocity_at_height"][self.language].format(
                angle=round(self.angle, 1),
                v0=round(self.v0, 1),
                h=h
            )
        
        return problem_text

    def solve(self):
        self.solution_steps = []
        
        if self.reasoning_mode:
            self.add_given(
                {"v₀": round(self.v0, 1), "α": round(self.angle, 1), "g": self.g},
                {"v₀": "м/с", "α": "°", "g": "м/с²"}
            )
        
        # Разложение скорости на составляющие
        if self.reasoning_mode:
            self.add_analysis("Разложим начальную скорость на горизонтальную и вертикальную составляющие." if self.language == "ru" else "Decompose initial velocity into horizontal and vertical components.")
        self.add_formula("vₓ = v₀·cos(α), vᵧ = v₀·sin(α)")
        self.add_substitution(f"vₓ = {round(self.v0, 1)}·cos({round(self.angle, 1)}°) = {round(self.vx, 2)} м/с")
        self.add_substitution(f"vᵧ = {round(self.v0, 1)}·sin({round(self.angle, 1)}°) = {round(self.vy, 2)} м/с")
        
        if self.task_type == "range":
            if self.reasoning_mode:
                self.add_find("L", "дальность полёта" if self.language == "ru" else "range")
            self.add_formula("L = v₀²·sin(2α)/g")
            self.add_substitution(f"L = {round(self.v0, 1)}²·sin(2×{round(self.angle, 1)}°)/{self.g}")
            self.add_calculation(f"{round(self.v0**2, 2)}×{round(math.sin(math.radians(2*self.angle)), 4)}/{self.g}", round(self.range_val, 2), "м")
            self.final_answer = f"L = {round(self.range_val, 2)} м"
            
        elif self.task_type == "max_height":
            if self.reasoning_mode:
                self.add_find("H", "максимальная высота" if self.language == "ru" else "maximum height")
            self.add_formula("H = v₀²·sin²(α)/(2g)")
            self.add_substitution(f"H = {round(self.v0, 1)}²·sin²({round(self.angle, 1)}°)/(2×{self.g})")
            self.add_calculation(f"{round(self.v0**2 * math.sin(math.radians(self.angle))**2, 2)}/{2*self.g}", round(self.max_height, 2), "м")
            self.final_answer = f"H = {round(self.max_height, 2)} м"
            
        elif self.task_type == "flight_time":
            if self.reasoning_mode:
                self.add_find("T", "время полёта" if self.language == "ru" else "flight time")
            self.add_formula("T = 2v₀·sin(α)/g")
            self.add_substitution(f"T = 2×{round(self.v0, 1)}·sin({round(self.angle, 1)}°)/{self.g}")
            self.add_calculation(f"2×{round(self.v0 * math.sin(math.radians(self.angle)), 2)}/{self.g}", round(self.flight_time, 2), "с")
            self.final_answer = f"T = {round(self.flight_time, 2)} с"
            
        else:  # velocity_at_height
            v_at_h = math.sqrt(self.v0**2 - 2 * self.g * self.height_query)
            if self.reasoning_mode:
                self.add_find("v", f"скорость на высоте {self.height_query} м" if self.language == "ru" else f"velocity at height {self.height_query} m")
            self.add_formula("v² = v₀² - 2gh → v = √(v₀² - 2gh)")
            self.add_substitution(f"v = √({round(self.v0, 1)}² - 2×{self.g}×{self.height_query})")
            self.add_calculation(f"√({round(self.v0**2 - 2*self.g*self.height_query, 2)})", round(v_at_h, 2), "м/с")
            self.final_answer = f"v = {round(v_at_h, 2)} м/с"
        
        if self.reasoning_mode:
            self.add_dimension_check("[м/с]²/[м/с²] = [м] ✓" if "м" in self.final_answer else "[м/с] ✓")

    def get_task_type(self):
        return "projectile_motion"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
