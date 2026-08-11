"""RelativisticEnergyTask — релятивистская энергия частиц.

Подтипы: кинетическая энергия, полная энергия, соотношение энергия–импульс.
Проверка числовая (в джоулях).
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class RelativisticEnergyTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Релятивистская кинетическая/полная энергия и связь E–p."""

    TASK_TYPE = "relativistic_energy"
    TASK_TYPES = ["kinetic", "total", "energy_momentum"]

    MASSES = {
        "electron": 9.1093837015e-31,
        "proton": 1.67262192369e-27,
        "neutron": 1.67492749804e-27,
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_beta": 0.3}, 2: {"max_beta": 0.4}, 3: {"max_beta": 0.5},
        4: {"max_beta": 0.6}, 5: {"max_beta": 0.7}, 6: {"max_beta": 0.8},
        7: {"max_beta": 0.9}, 8: {"max_beta": 0.95}, 9: {"max_beta": 0.98},
        10: {"max_beta": 0.99},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.c = get_constant("c")
        preset = self._interpolate_difficulty(difficulty)

        self.m = random.choice(list(self.MASSES.values()))
        self.beta = round(random.uniform(0.1, preset["max_beta"]), 2)
        # Импульс для energy_momentum на основе выбранных m и beta.
        gamma = 1 / math.sqrt(1 - self.beta ** 2)
        self.p = gamma * self.m * self.beta * self.c

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["relativistic_energy"]["problem"][self.task_type][language]
        if self.task_type == "energy_momentum":
            return p.format(m=fmt(self.m), p=fmt(self.p))
        return p.format(m=fmt(self.m), beta=self.beta)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["relativistic_energy"]["steps"]
        u = "Дж" if self.language == "ru" else "J"
        if self.task_type == "kinetic":
            gamma = 1 / math.sqrt(1 - self.beta ** 2)
            KE = (gamma - 1) * self.m * self.c ** 2
            self.solution_steps.append(steps["gamma_formula"][self.language])
            self.solution_steps.append(f"γ = 1/√(1−{self.beta}²) = {fmt(gamma)}")
            self.solution_steps.append(steps["kinetic_formula"][self.language])
            self.solution_steps.append(f"KE = (γ−1)·m·c² = {fmt(KE)} {u}")
            self.final_answer = f"KE = {fmt(KE)} {u}"
            self._answer_numbers = [KE]
        elif self.task_type == "total":
            gamma = 1 / math.sqrt(1 - self.beta ** 2)
            E = gamma * self.m * self.c ** 2
            self.solution_steps.append(steps["gamma_formula"][self.language])
            self.solution_steps.append(f"γ = 1/√(1−{self.beta}²) = {fmt(gamma)}")
            self.solution_steps.append(steps["total_formula"][self.language])
            self.solution_steps.append(f"E = γ·m·c² = {fmt(E)} {u}")
            self.final_answer = f"E = {fmt(E)} {u}"
            self._answer_numbers = [E]
        else:
            E = math.sqrt((self.p * self.c) ** 2 + (self.m * self.c ** 2) ** 2)
            self.solution_steps.append(steps["em_formula"][self.language])
            self.solution_steps.append(f"E = √((p·c)² + (m·c²)²) = {fmt(E)} {u}")
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
