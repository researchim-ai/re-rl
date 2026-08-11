"""MeanFreePathTask — средняя длина свободного пробега, концентрация, частота столкновений.

Проверка числовая с относительным допуском.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class MeanFreePathTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """λ = k_B·T/(√2·π·d²·P); n = P/(k_B·T); z = v/λ."""

    TASK_TYPE = "mean_free_path"
    TASK_TYPES = ["mean_free_path", "number_density", "collision_frequency"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_P": 101325, "max_T": 300}, 2: {"max_P": 200000, "max_T": 400},
        3: {"max_P": 300000, "max_T": 500}, 4: {"max_P": 500000, "max_T": 600},
        5: {"max_P": 1000000, "max_T": 700}, 6: {"max_P": 2000000, "max_T": 900},
        7: {"max_P": 5000000, "max_T": 1100}, 8: {"max_P": 10000000, "max_T": 1300},
        9: {"max_P": 20000000, "max_T": 1600}, 10: {"max_P": 50000000, "max_T": 2000},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "mean_free_path":
            self.d = round(random.uniform(2.0, 5.0), 2) * 1e-10  # диаметр, м
            self.P = random.randint(1000, preset["max_P"])
            self.T = random.randint(200, preset["max_T"])
        elif self.task_type == "number_density":
            self.P = random.randint(1000, preset["max_P"])
            self.T = random.randint(200, preset["max_T"])
        else:  # collision_frequency
            self.v = random.randint(200, 2000)
            self.lam = round(random.uniform(1e-8, 1e-6), 10)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["mean_free_path"]["problem"][self.task_type][language]
        if self.task_type == "mean_free_path":
            return p.format(d=fmt(self.d), P=self.P, T=self.T)
        if self.task_type == "number_density":
            return p.format(P=self.P, T=self.T)
        return p.format(v=self.v, lam=fmt(self.lam))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["mean_free_path"]["steps"]
        kB = get_constant("k_B")
        if self.task_type == "mean_free_path":
            lam = kB * self.T / (math.sqrt(2) * math.pi * self.d ** 2 * self.P)
            self.solution_steps.append(steps["mfp_formula"][self.language])
            self.solution_steps.append(
                f"λ = {fmt(kB)}·{self.T}/(√2·π·{fmt(self.d)}²·{self.P}) = {fmt(lam)} м")
            self.final_answer = f"λ = {fmt(lam)} м"
            self._answer_numbers = [lam]
        elif self.task_type == "number_density":
            n = self.P / (kB * self.T)
            self.solution_steps.append(steps["density_formula"][self.language])
            self.solution_steps.append(f"n = {self.P}/({fmt(kB)}·{self.T}) = {fmt(n)} м⁻³")
            self.final_answer = f"n = {fmt(n)} м⁻³"
            self._answer_numbers = [n]
        else:  # collision_frequency
            z = self.v / self.lam
            self.solution_steps.append(steps["frequency_formula"][self.language])
            self.solution_steps.append(f"z = {self.v}/{fmt(self.lam)} = {fmt(z)} с⁻¹")
            self.final_answer = f"z = {fmt(z)} с⁻¹"
            self._answer_numbers = [z]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
