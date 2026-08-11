"""StaticsEquilibriumTask — статика: равновесие рычага и балки на двух опорах.

Проверка числовая (по реакциям/силам) с относительным допуском.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class StaticsEquilibriumTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Равновесие: рычаг (моменты) и балка на двух опорах."""

    TASK_TYPE = "statics_equilibrium"
    TASK_TYPES = ["lever", "beam_supports"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_F": 40, "max_len": 3}, 2: {"max_F": 60, "max_len": 4},
        3: {"max_F": 80, "max_len": 5}, 4: {"max_F": 120, "max_len": 6},
        5: {"max_F": 160, "max_len": 7}, 6: {"max_F": 220, "max_len": 8},
        7: {"max_F": 300, "max_len": 9}, 8: {"max_F": 400, "max_len": 10},
        9: {"max_F": 550, "max_len": 12}, 10: {"max_F": 800, "max_len": 14},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "lever":
            self.F1 = random.randint(5, preset["max_F"])
            self.d1 = random.randint(1, preset["max_len"])
            self.d2 = random.randint(1, preset["max_len"])
        else:  # beam_supports
            self.L = random.randint(2, preset["max_len"])
            self.W = random.randint(10, preset["max_F"])
            self.P = random.randint(10, preset["max_F"])
            self.a = round(random.uniform(0.2, self.L - 0.2), 2)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["statics_equilibrium"]["problem"][self.task_type][language]
        if self.task_type == "lever":
            return p.format(F1=self.F1, d1=self.d1, d2=self.d2)
        return p.format(L=self.L, W=self.W, P=self.P, a=self.a)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["statics_equilibrium"]["steps"]
        u = "Н" if self.language == "ru" else "N"
        if self.task_type == "lever":
            F2 = self.F1 * self.d1 / self.d2
            self.solution_steps.append(steps["lever_formula"][self.language])
            self.solution_steps.append(f"F2 = {self.F1}·{self.d1}/{self.d2} = {fmt(F2)} {u}")
            self.final_answer = f"F2 = {fmt(F2)} {u}"
            self._answer_numbers = [F2]
        else:
            R2 = (self.W * (self.L / 2) + self.P * self.a) / self.L
            R1 = self.W + self.P - R2
            self.solution_steps.append(steps["beam_formula"][self.language])
            self.solution_steps.append(f"R2 = (W·L/2 + P·a)/L = {fmt(R2)} {u}")
            self.solution_steps.append(f"R1 = W + P − R2 = {fmt(R1)} {u}")
            self.final_answer = f"R1 = {fmt(R1)} {u}, R2 = {fmt(R2)} {u}"
            self._answer_numbers = [R1, R2]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
