"""SoundIntensityTask — интенсивность и уровень звука.

Подтипы: уровень в дБ по интенсивности, интенсивность по уровню, интенсивность
точечного источника на расстоянии. Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt

I0 = 1e-12  # порог слышимости, Вт/м²


class SoundIntensityTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Интенсивность и уровень звука."""

    TASK_TYPE = "sound_intensity"
    TASK_TYPES = ["decibel", "intensity_from_db", "point_source"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_exp": 3, "max_P": 1, "max_r": 5}, 2: {"max_exp": 4, "max_P": 2, "max_r": 8},
        3: {"max_exp": 5, "max_P": 5, "max_r": 10}, 4: {"max_exp": 6, "max_P": 10, "max_r": 15},
        5: {"max_exp": 7, "max_P": 20, "max_r": 20}, 6: {"max_exp": 8, "max_P": 50, "max_r": 30},
        7: {"max_exp": 9, "max_P": 100, "max_r": 50}, 8: {"max_exp": 10, "max_P": 200, "max_r": 80},
        9: {"max_exp": 11, "max_P": 500, "max_r": 120}, 10: {"max_exp": 12, "max_P": 1000, "max_r": 200},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        exp = random.randint(2, preset["max_exp"])
        self.I = round(random.uniform(1.0, 9.9), 2) * (10 ** (-exp))
        self.beta = random.randint(30, 120)
        self.P = round(random.uniform(0.1, preset["max_P"]), 2)
        self.r = round(random.uniform(1.0, preset["max_r"]), 1)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["sound_intensity"]["problem"][self.task_type][language]
        if self.task_type == "decibel":
            return p.format(I=fmt(self.I))
        if self.task_type == "intensity_from_db":
            return p.format(beta=self.beta)
        return p.format(P=self.P, r=self.r)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["sound_intensity"]["steps"]
        if self.task_type == "decibel":
            beta = 10 * math.log10(self.I / I0)
            self.solution_steps.append(steps["db_formula"][self.language])
            self.solution_steps.append(f"β = 10·log₁₀({fmt(self.I)}/1e-12) = {fmt(beta)} дБ")
            self.final_answer = f"β = {fmt(beta)} дБ" if self.language == "ru" else f"β = {fmt(beta)} dB"
            self._answer_numbers = [beta]
        elif self.task_type == "intensity_from_db":
            I = I0 * 10 ** (self.beta / 10)
            u = "Вт/м²" if self.language == "ru" else "W/m²"
            self.solution_steps.append(steps["inv_db_formula"][self.language])
            self.solution_steps.append(f"I = 1e-12·10^({self.beta}/10) = {fmt(I)} {u}")
            self.final_answer = f"I = {fmt(I)} {u}"
            self._answer_numbers = [I]
        else:
            I = self.P / (4 * math.pi * self.r ** 2)
            u = "Вт/м²" if self.language == "ru" else "W/m²"
            self.solution_steps.append(steps["source_formula"][self.language])
            self.solution_steps.append(f"I = {self.P}/(4π·{self.r}²) = {fmt(I)} {u}")
            self.final_answer = f"I = {fmt(I)} {u}"
            self._answer_numbers = [I]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
