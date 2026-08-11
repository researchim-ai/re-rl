"""GaussLawTask — теорема Гаусса для электростатики.

Подтипы: поток через замкнутую поверхность, заключённый заряд по потоку,
напряжённость поля точечного заряда. Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class GaussLawTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Теорема Гаусса."""

    TASK_TYPE = "gauss_law"
    TASK_TYPES = ["flux_charge", "enclosed_charge", "sphere_field"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_exp": 7, "max_r": 1}, 2: {"max_exp": 7, "max_r": 2},
        3: {"max_exp": 6, "max_r": 3}, 4: {"max_exp": 6, "max_r": 4},
        5: {"max_exp": 6, "max_r": 5}, 6: {"max_exp": 5, "max_r": 8},
        7: {"max_exp": 5, "max_r": 10}, 8: {"max_exp": 4, "max_r": 15},
        9: {"max_exp": 4, "max_r": 20}, 10: {"max_exp": 3, "max_r": 30},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.eps0 = get_constant("epsilon_0")
        self.k_e = get_constant("k_e")
        preset = self._interpolate_difficulty(difficulty)

        exp = random.randint(3, preset["max_exp"])
        self.Q = round(random.uniform(1.0, 9.9), 2) * (10 ** (-exp))
        self.flux = round(random.uniform(1.0, 9.9), 2) * (10 ** random.randint(2, 6))
        self.r = round(random.uniform(0.1, preset["max_r"]), 2)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["gauss_law"]["problem"][self.task_type][language]
        if self.task_type == "flux_charge":
            return p.format(Q=fmt(self.Q))
        if self.task_type == "enclosed_charge":
            return p.format(flux=fmt(self.flux))
        return p.format(r=self.r, Q=fmt(self.Q))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["gauss_law"]["steps"]
        if self.task_type == "flux_charge":
            flux = self.Q / self.eps0
            u = "В·м" if self.language == "ru" else "V·m"
            self.solution_steps.append(steps["flux_formula"][self.language])
            self.solution_steps.append(f"Φ = {fmt(self.Q)}/{self.eps0:.3e} = {fmt(flux)} {u}")
            self.final_answer = f"Φ = {fmt(flux)} {u}"
            self._answer_numbers = [flux]
        elif self.task_type == "enclosed_charge":
            Q = self.eps0 * self.flux
            u = "Кл" if self.language == "ru" else "C"
            self.solution_steps.append(steps["charge_formula"][self.language])
            self.solution_steps.append(f"Q = {self.eps0:.3e}·{fmt(self.flux)} = {fmt(Q)} {u}")
            self.final_answer = f"Q = {fmt(Q)} {u}"
            self._answer_numbers = [Q]
        else:
            E = self.k_e * self.Q / self.r ** 2
            u = "В/м" if self.language == "ru" else "V/m"
            self.solution_steps.append(steps["field_formula"][self.language])
            self.solution_steps.append(f"E = k·Q/r² = {fmt(E)} {u}")
            self.final_answer = f"E = {fmt(E)} {u}"
            self._answer_numbers = [E]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
