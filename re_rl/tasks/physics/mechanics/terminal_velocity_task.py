"""TerminalVelocityTask — установившаяся скорость при вязком/квадратичном сопротивлении.

Проверка числовая с относительным допуском.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class TerminalVelocityTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Стокс: v = 2r²(ρ_s−ρ_f)g/(9η), F = 6πηrv; квадратичное: v = √(2mg/(ρCA))."""

    TASK_TYPE = "terminal_velocity"
    TASK_TYPES = ["stokes_velocity", "drag_force", "quadratic_terminal"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_r": 1, "max_v": 2, "max_m": 1, "max_A": 0.5},
        2: {"max_r": 2, "max_v": 4, "max_m": 5, "max_A": 1},
        3: {"max_r": 3, "max_v": 6, "max_m": 10, "max_A": 1.5},
        4: {"max_r": 4, "max_v": 8, "max_m": 20, "max_A": 2},
        5: {"max_r": 5, "max_v": 10, "max_m": 40, "max_A": 3},
        6: {"max_r": 6, "max_v": 15, "max_m": 70, "max_A": 4},
        7: {"max_r": 8, "max_v": 20, "max_m": 100, "max_A": 5},
        8: {"max_r": 10, "max_v": 30, "max_m": 150, "max_A": 6},
        9: {"max_r": 12, "max_v": 40, "max_m": 250, "max_A": 8},
        10: {"max_r": 15, "max_v": 50, "max_m": 400, "max_A": 10},
    }

    # Вязкость среды, Па·с.
    FLUIDS = {
        "glycerin": {"eta": 1.5, "rho": 1260, "ru": "глицерин", "en": "glycerin"},
        "oil": {"eta": 0.1, "rho": 900, "ru": "масло", "en": "oil"},
        "water": {"eta": 1.0e-3, "rho": 1000, "ru": "вода", "en": "water"},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "stokes_velocity":
            fl = random.choice(list(self.FLUIDS.values()))
            self.eta = fl["eta"]
            self.rho_f = fl["rho"]
            self.rho_s = self.rho_f + random.randint(200, 6000)
            self.r = round(random.uniform(0.2, preset["max_r"]), 2)  # мм
        elif self.task_type == "drag_force":
            fl = random.choice(list(self.FLUIDS.values()))
            self.eta = fl["eta"]
            self.r = round(random.uniform(0.2, preset["max_r"]), 2)  # мм
            self.v = round(random.uniform(0.1, preset["max_v"]), 2)
        else:  # quadratic_terminal
            self.m = round(random.uniform(0.1, preset["max_m"]), 2)
            self.C = round(random.uniform(0.4, 1.2), 2)
            self.A = round(random.uniform(0.05, preset["max_A"]), 3)
            self.rho = 1.29

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["terminal_velocity"]["problem"][self.task_type][language]
        if self.task_type == "stokes_velocity":
            return p.format(r=self.r, rho_s=self.rho_s, rho_f=self.rho_f, eta=fmt(self.eta))
        if self.task_type == "drag_force":
            return p.format(r=self.r, v=self.v, eta=fmt(self.eta))
        return p.format(m=self.m, rho=self.rho, C=self.C, A=self.A)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["terminal_velocity"]["steps"]
        g = get_constant("g")
        if self.task_type == "stokes_velocity":
            r_m = self.r * 1e-3
            v = 2 * r_m ** 2 * (self.rho_s - self.rho_f) * g / (9 * self.eta)
            self.solution_steps.append(steps["stokes_v_formula"][self.language])
            self.solution_steps.append(
                f"v = 2·{fmt(r_m)}²·({self.rho_s}−{self.rho_f})·{g}/(9·{fmt(self.eta)}) = {fmt(v)} м/с")
            self.final_answer = f"v = {fmt(v)} м/с"
            self._answer_numbers = [v]
        elif self.task_type == "drag_force":
            r_m = self.r * 1e-3
            F = 6 * math.pi * self.eta * r_m * self.v
            self.solution_steps.append(steps["drag_formula"][self.language])
            self.solution_steps.append(
                f"F = 6π·{fmt(self.eta)}·{fmt(r_m)}·{self.v} = {fmt(F)} Н")
            self.final_answer = f"F = {fmt(F)} Н"
            self._answer_numbers = [F]
        else:  # quadratic_terminal
            v = math.sqrt(2 * self.m * g / (self.rho * self.C * self.A))
            self.solution_steps.append(steps["quadratic_formula"][self.language])
            self.solution_steps.append(
                f"v = √(2·{self.m}·{g}/({self.rho}·{self.C}·{self.A})) = {fmt(v)} м/с")
            self.final_answer = f"v = {fmt(v)} м/с"
            self._answer_numbers = [v]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
