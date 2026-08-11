"""RadiationPressureTask — давление света и импульс фотона.

Подтипы: импульс фотона p = h/λ, давление на поглощающую поверхность P = I/c,
давление на отражающую поверхность P = 2I/c. Проверка числовая.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class RadiationPressureTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Давление света и импульс фотона."""

    TASK_TYPE = "radiation_pressure"
    TASK_TYPES = ["photon_momentum", "pressure_absorbing", "pressure_reflecting"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_I": 100}, 2: {"max_I": 300}, 3: {"max_I": 500},
        4: {"max_I": 1000}, 5: {"max_I": 2000}, 6: {"max_I": 5000},
        7: {"max_I": 10000}, 8: {"max_I": 50000}, 9: {"max_I": 100000},
        10: {"max_I": 1000000},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.h = get_constant("h")
        self.c = get_constant("c")
        preset = self._interpolate_difficulty(difficulty)

        self.lam = round(random.uniform(1.0, 9.9), 2) * 1e-7  # видимый/УФ диапазон
        self.I = round(random.uniform(10.0, preset["max_I"]), 1)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["radiation_pressure"]["problem"][self.task_type][language]
        if self.task_type == "photon_momentum":
            return p.format(lam=fmt(self.lam))
        return p.format(I=fmt(self.I))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["radiation_pressure"]["steps"]
        if self.task_type == "photon_momentum":
            p_val = self.h / self.lam
            u = "кг·м/с" if self.language == "ru" else "kg·m/s"
            self.solution_steps.append(steps["momentum_formula"][self.language])
            self.solution_steps.append(f"p = {self.h:.3e}/{fmt(self.lam)} = {fmt(p_val)} {u}")
            self.final_answer = f"p = {fmt(p_val)} {u}"
            self._answer_numbers = [p_val]
        elif self.task_type == "pressure_absorbing":
            P = self.I / self.c
            u = "Па" if self.language == "ru" else "Pa"
            self.solution_steps.append(steps["absorbing_formula"][self.language])
            self.solution_steps.append(f"P = {fmt(self.I)}/{self.c:.3e} = {fmt(P)} {u}")
            self.final_answer = f"P = {fmt(P)} {u}"
            self._answer_numbers = [P]
        else:
            P = 2 * self.I / self.c
            u = "Па" if self.language == "ru" else "Pa"
            self.solution_steps.append(steps["reflecting_formula"][self.language])
            self.solution_steps.append(f"P = 2·{fmt(self.I)}/{self.c:.3e} = {fmt(P)} {u}")
            self.final_answer = f"P = {fmt(P)} {u}"
            self._answer_numbers = [P]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
