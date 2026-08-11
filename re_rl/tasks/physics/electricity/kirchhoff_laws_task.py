"""KirchhoffLawsTask — правила Кирхгофа для цепей с несколькими ЭДС.

Подтипы: одиночный контур (две встречные ЭДС) и двухконтурная схема
(ток через общий резистор). Проверка числовая по току.
"""

import random
from typing import Any, ClassVar, Dict

import numpy as np

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class KirchhoffLawsTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Расчёт токов по правилам Кирхгофа."""

    TASK_TYPE = "kirchhoff_laws"
    TASK_TYPES = ["single_loop", "two_loop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_E": 6, "max_R": 5}, 2: {"max_E": 9, "max_R": 8},
        3: {"max_E": 12, "max_R": 10}, 4: {"max_E": 15, "max_R": 15},
        5: {"max_E": 24, "max_R": 20}, 6: {"max_E": 36, "max_R": 30},
        7: {"max_E": 48, "max_R": 40}, 8: {"max_E": 60, "max_R": 50},
        9: {"max_E": 100, "max_R": 80}, 10: {"max_E": 220, "max_R": 100},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.E1 = random.randint(2, preset["max_E"])
        self.E2 = random.randint(2, preset["max_E"])
        self.R1 = random.randint(1, preset["max_R"])
        self.R2 = random.randint(1, preset["max_R"])
        self.R3 = random.randint(1, preset["max_R"])

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["kirchhoff_laws"]["problem"][self.task_type][language]
        if self.task_type == "single_loop":
            return p.format(E1=self.E1, E2=self.E2, R1=self.R1, R2=self.R2)
        return p.format(E1=self.E1, E2=self.E2, R1=self.R1, R2=self.R2, R3=self.R3)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["kirchhoff_laws"]["steps"]
        u = "А" if self.language == "ru" else "A"
        if self.task_type == "single_loop":
            I = (self.E1 - self.E2) / (self.R1 + self.R2)
            self.solution_steps.append(steps["single_formula"][self.language])
            self.solution_steps.append(
                f"I = ({self.E1} − {self.E2})/({self.R1} + {self.R2}) = {fmt(I)} {u}")
            self.final_answer = f"I = {fmt(I)} {u}"
            self._answer_numbers = [I]
        else:
            # I1, I2, I3
            A = np.array([[self.R1, 0.0, self.R3],
                          [0.0, self.R2, self.R3],
                          [1.0, 1.0, -1.0]])
            b = np.array([self.E1, self.E2, 0.0])
            I1, I2, I3 = np.linalg.solve(A, b)
            self.solution_steps.append(steps["two_formula"][self.language])
            self.solution_steps.append(f"I1 = {fmt(I1)} {u}, I2 = {fmt(I2)} {u}")
            self.solution_steps.append(f"I3 = I1 + I2 = {fmt(I3)} {u}")
            self.final_answer = f"I3 = {fmt(I3)} {u}"
            self._answer_numbers = [float(I3)]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
