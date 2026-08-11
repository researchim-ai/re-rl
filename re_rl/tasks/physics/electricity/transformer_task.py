"""TransformerTask — идеальный трансформатор и его КПД.

Подтипы: отношение напряжений, отношение токов, КПД. Проверка числовая.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class TransformerTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Трансформатор: напряжения, токи, КПД."""

    TASK_TYPE = "transformer"
    TASK_TYPES = ["voltage_ratio", "current_ratio", "efficiency"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_N": 200, "max_U": 50}, 2: {"max_N": 400, "max_U": 100},
        3: {"max_N": 600, "max_U": 220}, 4: {"max_N": 1000, "max_U": 380},
        5: {"max_N": 1500, "max_U": 500}, 6: {"max_N": 2000, "max_U": 1000},
        7: {"max_N": 3000, "max_U": 2000}, 8: {"max_N": 5000, "max_U": 5000},
        9: {"max_N": 8000, "max_U": 10000}, 10: {"max_N": 12000, "max_U": 20000},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.N1 = random.randint(50, preset["max_N"])
        self.N2 = random.randint(50, preset["max_N"])
        self.U1 = random.randint(10, preset["max_U"])
        self.I1 = round(random.uniform(0.5, 20.0), 2)
        self.P1 = random.randint(100, 5000)
        self.P2 = random.randint(50, self.P1)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["transformer"]["problem"][self.task_type][language]
        if self.task_type == "voltage_ratio":
            return p.format(N1=self.N1, N2=self.N2, U1=self.U1)
        if self.task_type == "current_ratio":
            return p.format(N1=self.N1, N2=self.N2, I1=self.I1)
        return p.format(P1=self.P1, P2=self.P2)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["transformer"]["steps"]
        if self.task_type == "voltage_ratio":
            U2 = self.U1 * self.N2 / self.N1
            u = "В" if self.language == "ru" else "V"
            self.solution_steps.append(steps["voltage_formula"][self.language])
            self.solution_steps.append(f"U2 = {self.U1}·{self.N2}/{self.N1} = {fmt(U2)} {u}")
            self.final_answer = f"U2 = {fmt(U2)} {u}"
            self._answer_numbers = [U2]
        elif self.task_type == "current_ratio":
            I2 = self.I1 * self.N1 / self.N2
            u = "А" if self.language == "ru" else "A"
            self.solution_steps.append(steps["current_formula"][self.language])
            self.solution_steps.append(f"I2 = {self.I1}·{self.N1}/{self.N2} = {fmt(I2)} {u}")
            self.final_answer = f"I2 = {fmt(I2)} {u}"
            self._answer_numbers = [I2]
        else:
            eta = self.P2 / self.P1 * 100
            self.solution_steps.append(steps["efficiency_formula"][self.language])
            self.solution_steps.append(f"η = {self.P2}/{self.P1}·100% = {fmt(eta)}%")
            self.final_answer = f"η = {fmt(eta)}%"
            self._answer_numbers = [eta]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
