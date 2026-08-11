"""RLCircuitsTask — переходные процессы в RL-цепи.

Подтипы: постоянная времени τ = L/R, установившийся ток I = E/R,
ток i(t) при нарастании. Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class RLCircuitsTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """RL-цепь: τ, установившийся ток, i(t)."""

    TASK_TYPE = "rl_circuits"
    TASK_TYPES = ["time_constant", "final_current", "current_growth"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_R": 10, "max_E": 12}, 2: {"max_R": 20, "max_E": 24},
        3: {"max_R": 50, "max_E": 36}, 4: {"max_R": 100, "max_E": 48},
        5: {"max_R": 200, "max_E": 60}, 6: {"max_R": 500, "max_E": 100},
        7: {"max_R": 1000, "max_E": 150}, 8: {"max_R": 2000, "max_E": 220},
        9: {"max_R": 5000, "max_E": 300}, 10: {"max_R": 10000, "max_E": 400},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.R = random.randint(2, preset["max_R"])
        self.L = round(random.uniform(0.01, 2.0), 3)
        self.E = random.randint(3, preset["max_E"])
        tau = self.L / self.R
        self.t = round(random.uniform(0.2, 3.0) * tau, 6)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["rl_circuits"]["problem"][self.task_type][language]
        if self.task_type == "time_constant":
            return p.format(L=self.L, R=self.R)
        if self.task_type == "final_current":
            return p.format(R=self.R, L=self.L, E=self.E)
        return p.format(E=self.E, R=self.R, L=self.L, t=fmt(self.t))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["rl_circuits"]["steps"]
        if self.task_type == "time_constant":
            tau = self.L / self.R
            u = "с" if self.language == "ru" else "s"
            self.solution_steps.append(steps["tau_formula"][self.language])
            self.solution_steps.append(f"τ = {self.L}/{self.R} = {fmt(tau)} {u}")
            self.final_answer = f"τ = {fmt(tau)} {u}"
            self._answer_numbers = [tau]
        elif self.task_type == "final_current":
            I = self.E / self.R
            u = "А" if self.language == "ru" else "A"
            self.solution_steps.append(steps["final_formula"][self.language])
            self.solution_steps.append(f"I = {self.E}/{self.R} = {fmt(I)} {u}")
            self.final_answer = f"I = {fmt(I)} {u}"
            self._answer_numbers = [I]
        else:
            i = (self.E / self.R) * (1 - math.exp(-self.t * self.R / self.L))
            u = "А" if self.language == "ru" else "A"
            self.solution_steps.append(steps["growth_formula"][self.language])
            self.solution_steps.append(
                f"i = ({self.E}/{self.R})·(1 − e^(−{fmt(self.t)}·{self.R}/{self.L})) = {fmt(i)} {u}")
            self.final_answer = f"i = {fmt(i)} {u}"
            self._answer_numbers = [i]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
