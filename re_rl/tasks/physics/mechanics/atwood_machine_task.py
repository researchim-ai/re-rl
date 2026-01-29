# re_rl/tasks/physics/mechanics/atwood_machine_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS


class AtwoodMachineTask(BaseMathTask):
    """
    Задачи на машину Атвуда (система блоков).
    
    Типы задач:
    - basic: базовая задача (два груза через блок)
    - with_pulley_mass: с учётом массы блока
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"mass_range": (1, 5), "task_type": "basic"},
        3: {"mass_range": (2, 10), "task_type": "basic"},
        5: {"mass_range": (5, 20), "task_type": "basic"},
        7: {"mass_range": (5, 30), "task_type": "with_pulley_mass"},
        10: {"mass_range": (10, 50), "task_type": "with_pulley_mass"},
    }
    
    TASK_TYPES = ["basic", "with_pulley_mass"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        m1: float = None,
        m2: float = None,
        M_pulley: float = None,
        R_pulley: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text"
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            mass_range = preset.get("mass_range", (5, 20))
            task_type = task_type or preset.get("task_type", "basic")
        else:
            mass_range = (5, 20)
            task_type = task_type or "basic"
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type
        
        # Генерируем массы (m1 > m2 для определённости)
        self.m1 = m1 or round(random.uniform(*mass_range), 1)
        self.m2 = m2 or round(random.uniform(mass_range[0], self.m1 * 0.9), 1)
        if self.m1 < self.m2:
            self.m1, self.m2 = self.m2, self.m1
        
        self.M_pulley = M_pulley or round(random.uniform(0.5, 5), 2)
        self.R_pulley = R_pulley or round(random.uniform(0.05, 0.3), 2)
        
        self.g = PHYSICS_CONSTANTS["g"]["value"]
        
        # Вычисляем
        self._calculate()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)

    def _calculate(self):
        """Вычисляет ускорение и натяжение."""
        if self.task_type == "basic":
            # a = (m1 - m2)g / (m1 + m2)
            self.acceleration = (self.m1 - self.m2) * self.g / (self.m1 + self.m2)
            # T = 2*m1*m2*g / (m1 + m2)
            self.tension = 2 * self.m1 * self.m2 * self.g / (self.m1 + self.m2)
        else:
            # С учётом момента инерции блока I = MR²/2
            # a = (m1 - m2)g / (m1 + m2 + M/2)
            self.acceleration = (self.m1 - self.m2) * self.g / (self.m1 + self.m2 + self.M_pulley / 2)
            self.tension = self.m1 * (self.g - self.acceleration)

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["atwood_machine"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "basic":
            problem_text += templates["problem"]["basic"][self.language].format(
                m1=self.m1,
                m2=self.m2
            )
        else:
            problem_text += templates["problem"]["with_pulley_mass"][self.language].format(
                m1=self.m1,
                m2=self.m2,
                M=self.M_pulley,
                R=self.R_pulley
            )
        
        return problem_text

    def solve(self):
        templates = PROMPT_TEMPLATES["atwood_machine"]
        steps = []
        
        # Уравнения движения
        steps.append(templates["steps"]["equations"][self.language])
        
        # Ускорение
        steps.append(templates["steps"]["acceleration"][self.language].format(
            a=round(self.acceleration, 3)
        ))
        
        # Натяжение
        steps.append(templates["steps"]["tension"][self.language].format(
            T=round(self.tension, 2)
        ))
        
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps[:self.detail_level]
        self.final_answer = templates["final_answer"][self.language].format(
            a=round(self.acceleration, 3),
            T=round(self.tension, 2)
        )

    def get_task_type(self):
        return "atwood_machine"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
