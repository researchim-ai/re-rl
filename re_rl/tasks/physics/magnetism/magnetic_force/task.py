from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/physics/magnetism/magnetic_force_task.py

import random
import math
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import PHYSICS_CONSTANTS


class MagneticForceTask(BaseMathTask):
    """
    Задачи на движение заряда в магнитном поле (сила Лоренца).
    
    Типы задач:
    - lorentz_force: сила Лоренца
    - radius: радиус траектории
    - period: период обращения
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"B_range": (0.01, 0.1), "v_range": (1e5, 1e6)},
        3: {"B_range": (0.05, 0.5), "v_range": (1e5, 5e6)},
        5: {"B_range": (0.1, 1.0), "v_range": (1e6, 1e7)},
        7: {"B_range": (0.5, 2.0), "v_range": (1e6, 5e7)},
        10: {"B_range": (1.0, 5.0), "v_range": (1e7, 1e8)},
    }
    
    TASK_TYPES = ["lorentz_force", "radius", "period"]
    
    PARTICLES = {
        "electron": {"mass": 9.109e-31, "charge": 1.602e-19, "name_ru": texts.literal('literals.s0'), "name_en": "electron"},
        "proton": {"mass": 1.673e-27, "charge": 1.602e-19, "name_ru": texts.literal('literals.s1'), "name_en": "proton"},
        "alpha": {"mass": 6.645e-27, "charge": 3.204e-19, "name_ru": texts.literal('literals.s2'), "name_en": "alpha particle"},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        task_type: str = None,
        particle: str = None,
        B: float = None,
        v: float = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            B_range = preset.get("B_range", (0.1, 1.0))
            v_range = preset.get("v_range", (1e6, 1e7))
        else:
            B_range = (0.1, 1.0)
            v_range = (1e6, 1e7)
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        self.particle = particle or random.choice(list(self.PARTICLES.keys()))
        
        self.B = B or round(random.uniform(*B_range), 3)
        self.v = v or random.uniform(*v_range)
        
        # Параметры частицы
        self.m = self.PARTICLES[self.particle]["mass"]
        self.q = self.PARTICLES[self.particle]["charge"]
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_text(self) -> str:
        templates = PROMPT_TEMPLATES["magnetic_force"]
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        
        if self.task_type == "lorentz_force":
            problem_text += templates["problem"]["lorentz_force"][self.language].format(
                q=f"{self.q:.3e}",
                v=f"{self.v:.3e}",
                B=self.B
            )
        elif self.task_type == "radius":
            problem_text += templates["problem"]["radius"][self.language].format(
                m=f"{self.m:.3e}",
                q=f"{self.q:.3e}",
                v=f"{self.v:.3e}",
                B=self.B
            )
        else:  # period
            problem_text += templates["problem"]["period"][self.language].format(
                m=f"{self.m:.3e}",
                q=f"{self.q:.3e}",
                B=self.B
            )
        
        return problem_text

    def solve(self):
        templates = PROMPT_TEMPLATES["magnetic_force"]
        steps = []
        
        if self.task_type == "lorentz_force":
            steps.append(templates["steps"]["lorentz"][self.language])
            F = self.q * self.v * self.B
            steps.append(texts.t('s4', self.language, q=self.q, v=self.v, B=self.B, F=F))
            answer = texts.t('s3', self.language, F=F)
            
        elif self.task_type == "radius":
            steps.append(templates["steps"]["radius_formula"][self.language])
            r = self.m * self.v / (self.q * self.B)
            steps.append(texts.t('s7', self.language, m=self.m, v=self.v, q=self.q, B=self.B, r=r))
            answer = texts.t('s5', self.language, r=r, v1=r * 100)
            
        else:  # period
            steps.append(templates["steps"]["period_formula"][self.language])
            T = 2 * math.pi * self.m / (self.q * self.B)
            steps.append(texts.t('s8', self.language, m=self.m, q=self.q, B=self.B, T=T))
            answer = texts.t('s6', self.language, T=T)
        
        self.solution_steps = steps
        self.final_answer = templates["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "magnetic_force"
    
    @classmethod
    def generate_random_task(cls, reasoning_mode: bool = False, **kwargs):
        return cls(reasoning_mode=reasoning_mode, **kwargs)
