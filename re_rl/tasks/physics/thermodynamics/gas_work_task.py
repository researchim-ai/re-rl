"""GasWorkTask — работа газа в процессах и первое начало термодинамики.

Проверка числовая с относительным допуском.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class GasWorkTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """W = P·ΔV (изобара); W = nRT·ln(V2/V1) (изотерма); ΔU = Q − W."""

    TASK_TYPE = "gas_work"
    TASK_TYPES = ["isobaric_work", "isothermal_work", "first_law"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_P": 100000, "max_n": 2, "max_T": 400, "max_Q": 1000},
        2: {"max_P": 200000, "max_n": 3, "max_T": 500, "max_Q": 2000},
        3: {"max_P": 300000, "max_n": 5, "max_T": 600, "max_Q": 5000},
        4: {"max_P": 500000, "max_n": 8, "max_T": 700, "max_Q": 10000},
        5: {"max_P": 1000000, "max_n": 10, "max_T": 800, "max_Q": 20000},
        6: {"max_P": 2000000, "max_n": 15, "max_T": 900, "max_Q": 50000},
        7: {"max_P": 3000000, "max_n": 20, "max_T": 1000, "max_Q": 100000},
        8: {"max_P": 5000000, "max_n": 30, "max_T": 1200, "max_Q": 200000},
        9: {"max_P": 8000000, "max_n": 50, "max_T": 1500, "max_Q": 500000},
        10: {"max_P": 10000000, "max_n": 80, "max_T": 2000, "max_Q": 1000000},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "isobaric_work":
            self.P = random.randint(50000, preset["max_P"])
            self.V1 = round(random.uniform(0.01, 1.0), 3)
            self.V2 = round(self.V1 + random.uniform(0.01, 2.0), 3)
        elif self.task_type == "isothermal_work":
            self.n = random.randint(1, preset["max_n"])
            self.T = random.randint(250, preset["max_T"])
            self.V1 = round(random.uniform(0.01, 1.0), 3)
            self.V2 = round(self.V1 * random.uniform(1.5, 4.0), 3)
        else:  # first_law
            self.Q = random.randint(-preset["max_Q"], preset["max_Q"])
            self.W = random.randint(-preset["max_Q"], preset["max_Q"])
            while self.W == self.Q:  # избегаем ΔU = 0 (сложно проверять с rtol)
                self.W = random.randint(-preset["max_Q"], preset["max_Q"])

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["gas_work"]["problem"][self.task_type][language]
        if self.task_type == "isobaric_work":
            return p.format(P=self.P, V1=self.V1, V2=self.V2)
        if self.task_type == "isothermal_work":
            return p.format(n=self.n, T=self.T, V1=self.V1, V2=self.V2)
        return p.format(Q=self.Q, W=self.W)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["gas_work"]["steps"]
        if self.task_type == "isobaric_work":
            W = self.P * (self.V2 - self.V1)
            self.solution_steps.append(steps["isobaric_formula"][self.language])
            self.solution_steps.append(
                f"W = {self.P}·({self.V2}−{self.V1}) = {fmt(W)} Дж")
            self.final_answer = f"W = {fmt(W)} Дж"
            self._answer_numbers = [W]
        elif self.task_type == "isothermal_work":
            R = get_constant("R")
            W = self.n * R * self.T * math.log(self.V2 / self.V1)
            self.solution_steps.append(steps["isothermal_formula"][self.language])
            self.solution_steps.append(
                f"W = {self.n}·{R}·{self.T}·ln({self.V2}/{self.V1}) = {fmt(W)} Дж")
            self.final_answer = f"W = {fmt(W)} Дж"
            self._answer_numbers = [W]
        else:  # first_law
            dU = self.Q - self.W
            self.solution_steps.append(steps["first_law_formula"][self.language])
            self.solution_steps.append(f"ΔU = {self.Q} − ({self.W}) = {fmt(dU)} Дж")
            self.final_answer = f"ΔU = {fmt(dU)} Дж"
            self._answer_numbers = [dU]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
