"""KineticTheoryTask — молекулярно-кинетическая теория газов.

Подтипы: среднеквадратичная скорость, средняя кинетическая энергия молекулы,
внутренняя энергия одноатомного газа. Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class KineticTheoryTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """МКТ: v_rms, средняя энергия, внутренняя энергия."""

    TASK_TYPE = "kinetic_theory"
    TASK_TYPES = ["rms_speed", "mean_ke", "internal_energy"]

    GASES = {
        "H2": {"M": 0.002016, "ru": "водород", "en": "hydrogen"},
        "He": {"M": 0.004003, "ru": "гелий", "en": "helium"},
        "N2": {"M": 0.028014, "ru": "азот", "en": "nitrogen"},
        "O2": {"M": 0.031998, "ru": "кислород", "en": "oxygen"},
        "CO2": {"M": 0.044010, "ru": "углекислый газ", "en": "carbon dioxide"},
        "Ar": {"M": 0.039948, "ru": "аргон", "en": "argon"},
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_T": 350, "max_n": 2}, 2: {"max_T": 450, "max_n": 3},
        3: {"max_T": 550, "max_n": 4}, 4: {"max_T": 700, "max_n": 5},
        5: {"max_T": 900, "max_n": 6}, 6: {"max_T": 1100, "max_n": 8},
        7: {"max_T": 1400, "max_n": 10}, 8: {"max_T": 1800, "max_n": 12},
        9: {"max_T": 2200, "max_n": 15}, 10: {"max_T": 3000, "max_n": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.R = get_constant("R")
        self.k_B = get_constant("k_B")
        preset = self._interpolate_difficulty(difficulty)

        self.T = random.randint(200, preset["max_T"])
        self.n = random.randint(1, preset["max_n"])
        self.gas_key = random.choice(list(self.GASES.keys()))
        self.M = self.GASES[self.gas_key]["M"]

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["kinetic_theory"]["problem"][self.task_type][language]
        gas = self.GASES[self.gas_key][language]
        if self.task_type == "rms_speed":
            return p.format(gas=gas, M=self.M, T=self.T)
        if self.task_type == "mean_ke":
            return p.format(T=self.T)
        return p.format(n=self.n, T=self.T)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["kinetic_theory"]["steps"]
        if self.task_type == "rms_speed":
            v = math.sqrt(3 * self.R * self.T / self.M)
            u = "м/с" if self.language == "ru" else "m/s"
            self.solution_steps.append(steps["rms_formula"][self.language])
            self.solution_steps.append(f"v_rms = √(3·{self.R:.3f}·{self.T}/{self.M}) = {fmt(v)} {u}")
            self.final_answer = f"v_rms = {fmt(v)} {u}"
            self._answer_numbers = [v]
        elif self.task_type == "mean_ke":
            E = 1.5 * self.k_B * self.T
            self.solution_steps.append(steps["ke_formula"][self.language])
            self.solution_steps.append(f"⟨E⟩ = 1.5·{self.k_B:.3e}·{self.T} = {fmt(E)} Дж")
            self.final_answer = f"{fmt(E)} Дж" if self.language == "ru" else f"{fmt(E)} J"
            self._answer_numbers = [E]
        else:
            U = 1.5 * self.n * self.R * self.T
            self.solution_steps.append(steps["u_formula"][self.language])
            self.solution_steps.append(f"U = 1.5·{self.n}·{self.R:.3f}·{self.T} = {fmt(U)} Дж")
            self.final_answer = f"U = {fmt(U)} Дж" if self.language == "ru" else f"U = {fmt(U)} J"
            self._answer_numbers = [U]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
