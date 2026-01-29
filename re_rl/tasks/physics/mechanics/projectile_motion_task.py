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
        output_format: OutputFormat = "text"
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
        templates = PROMPT_TEMPLATES["projectile_motion"]
        steps = []
        
        # Шаг 1: разложение скорости
        step1 = templates["steps"]["decompose"][self.language].format(
            vx=round(self.vx, 2),
            vy=round(self.vy, 2)
        )
        steps.append(step1)
        
        if self.task_type == "range":
            step2 = templates["steps"]["range_formula"][self.language]
            steps.append(step2)
            result = round(self.range_val, 2)
            self.final_answer = templates["final_answer"][self.language].format(
                answer=f"L = {result} м"
            )
        elif self.task_type == "max_height":
            step2 = templates["steps"]["height_formula"][self.language]
            steps.append(step2)
            result = round(self.max_height, 2)
            self.final_answer = templates["final_answer"][self.language].format(
                answer=f"H = {result} м"
            )
        elif self.task_type == "flight_time":
            step2 = templates["steps"]["time_formula"][self.language]
            steps.append(step2)
            result = round(self.flight_time, 2)
            self.final_answer = templates["final_answer"][self.language].format(
                answer=f"T = {result} с"
            )
        else:  # velocity_at_height
            # v² = v₀² - 2gh
            v_at_h = math.sqrt(self.v0**2 - 2 * self.g * self.height_query)
            result = round(v_at_h, 2)
            self.final_answer = templates["final_answer"][self.language].format(
                answer=f"v = {result} м/с"
            )
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps[:self.detail_level]

    def get_task_type(self):
        return "projectile_motion"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
