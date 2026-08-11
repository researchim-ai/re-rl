"""BlackbodyRadiationTask — излучение абсолютно чёрного тела.

Подтипы: закон смещения Вина (λ_max по T и T по λ_max) и закон
Стефана–Больцмана (мощность). Проверка числовая.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt

WIEN_B = 2.897771955e-3  # постоянная закона смещения Вина, м·К


class BlackbodyRadiationTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Излучение чёрного тела: Вин и Стефан–Больцман."""

    TASK_TYPE = "blackbody_radiation"
    TASK_TYPES = ["wien", "temperature_from_wien", "stefan"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_T": 1000, "max_A": 1}, 2: {"max_T": 2000, "max_A": 2},
        3: {"max_T": 3000, "max_A": 3}, 4: {"max_T": 4000, "max_A": 5},
        5: {"max_T": 5000, "max_A": 8}, 6: {"max_T": 6000, "max_A": 10},
        7: {"max_T": 8000, "max_A": 15}, 8: {"max_T": 10000, "max_A": 20},
        9: {"max_T": 15000, "max_A": 30}, 10: {"max_T": 20000, "max_A": 50},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.sigma = get_constant("sigma")
        preset = self._interpolate_difficulty(difficulty)

        self.T = random.randint(300, preset["max_T"])
        self.A = round(random.uniform(0.1, preset["max_A"]), 2)
        self.lam = round(WIEN_B / self.T, 12)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["blackbody_radiation"]["problem"][self.task_type][language]
        if self.task_type == "wien":
            return p.format(T=self.T)
        if self.task_type == "temperature_from_wien":
            return p.format(lam=fmt(self.lam))
        return p.format(A=self.A, T=self.T)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["blackbody_radiation"]["steps"]
        if self.task_type == "wien":
            lam = WIEN_B / self.T
            u = "м" if self.language == "ru" else "m"
            self.solution_steps.append(steps["wien_formula"][self.language])
            self.solution_steps.append(f"λ_max = 2.898e-3/{self.T} = {fmt(lam)} {u}")
            self.final_answer = f"λ_max = {fmt(lam)} {u}"
            self._answer_numbers = [lam]
        elif self.task_type == "temperature_from_wien":
            T = WIEN_B / self.lam
            u = "К" if self.language == "ru" else "K"
            self.solution_steps.append(steps["temp_formula"][self.language])
            self.solution_steps.append(f"T = 2.898e-3/{fmt(self.lam)} = {fmt(T)} {u}")
            self.final_answer = f"T = {fmt(T)} {u}"
            self._answer_numbers = [T]
        else:
            P = self.sigma * self.A * self.T ** 4
            u = "Вт" if self.language == "ru" else "W"
            self.solution_steps.append(steps["stefan_formula"][self.language])
            self.solution_steps.append(f"P = {self.sigma:.3e}·{self.A}·{self.T}⁴ = {fmt(P)} {u}")
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
