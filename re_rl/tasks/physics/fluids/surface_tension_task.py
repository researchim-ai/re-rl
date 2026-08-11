"""SurfaceTensionTask — поверхностное натяжение: капиллярный подъём, давление Лапласа, сила.

Проверка числовая с относительным допуском.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class SurfaceTensionTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """h = 2σ/(ρgr); ΔP = kσ/r (k=2 капля, k=4 мыльный пузырь); F = 2σL."""

    TASK_TYPE = "surface_tension"
    TASK_TYPES = ["capillary_rise", "laplace_pressure", "wire_force"]

    LIQUIDS = {
        "water": {"sigma": 0.0728, "rho": 1000, "ru": "вода", "en": "water"},
        "mercury": {"sigma": 0.465, "rho": 13600, "ru": "ртуть", "en": "mercury"},
        "ethanol": {"sigma": 0.0223, "rho": 789, "ru": "этанол", "en": "ethanol"},
        "glycerin": {"sigma": 0.063, "rho": 1260, "ru": "глицерин", "en": "glycerin"},
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_r": 2, "max_L": 5}, 2: {"max_r": 3, "max_L": 8},
        3: {"max_r": 4, "max_L": 10}, 4: {"max_r": 5, "max_L": 15},
        5: {"max_r": 6, "max_L": 20}, 6: {"max_r": 8, "max_L": 30},
        7: {"max_r": 10, "max_L": 40}, 8: {"max_r": 12, "max_L": 50},
        9: {"max_r": 15, "max_L": 70}, 10: {"max_r": 20, "max_L": 100},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        liq = random.choice(list(self.LIQUIDS.values()))
        self._liq = liq

        if self.task_type == "capillary_rise":
            self.r = round(random.uniform(0.1, preset["max_r"]), 2)  # мм
            self.sigma = liq["sigma"]
            self.rho = liq["rho"]
        elif self.task_type == "laplace_pressure":
            self.r = round(random.uniform(0.1, preset["max_r"]), 2)  # мм
            self.sigma = liq["sigma"]
            # k=2 — жидкая капля (одна поверхность), k=4 — мыльный пузырь (две).
            self._bubble = random.random() < 0.5
            self.k = 4 if self._bubble else 2
        else:  # wire_force
            self.L = round(random.uniform(1, preset["max_L"]), 2)  # см
            self.sigma = liq["sigma"]

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["surface_tension"]["problem"][self.task_type][language]
        if self.task_type == "capillary_rise":
            return p.format(r=self.r, sigma=self.sigma, rho=self.rho)
        if self.task_type == "laplace_pressure":
            if language == "ru":
                obj = "мыльного пузыря" if self._bubble else "капли"
            else:
                obj = "soap bubble" if self._bubble else "droplet"
            return p.format(obj=obj, r=self.r, sigma=self.sigma)
        return p.format(L=self.L, sigma=self.sigma)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["surface_tension"]["steps"]
        g = get_constant("g")
        if self.task_type == "capillary_rise":
            r_m = self.r * 1e-3
            h = 2 * self.sigma / (self.rho * g * r_m)
            self.solution_steps.append(steps["capillary_formula"][self.language])
            self.solution_steps.append(
                f"h = 2·{self.sigma}/({self.rho}·{g}·{fmt(r_m)}) = {fmt(h)} м")
            self.final_answer = f"h = {fmt(h)} м"
            self._answer_numbers = [h]
        elif self.task_type == "laplace_pressure":
            r_m = self.r * 1e-3
            dP = self.k * self.sigma / r_m
            self.solution_steps.append(steps["laplace_formula"][self.language].format(k=self.k))
            self.solution_steps.append(f"ΔP = {self.k}·{self.sigma}/{fmt(r_m)} = {fmt(dP)} Па")
            self.final_answer = f"ΔP = {fmt(dP)} Па"
            self._answer_numbers = [dP]
        else:  # wire_force
            L_m = self.L * 1e-2
            F = 2 * self.sigma * L_m
            self.solution_steps.append(steps["wire_formula"][self.language])
            self.solution_steps.append(f"F = 2·{self.sigma}·{fmt(L_m)} = {fmt(F)} Н")
            self.final_answer = f"F = {fmt(F)} Н"
            self._answer_numbers = [F]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
