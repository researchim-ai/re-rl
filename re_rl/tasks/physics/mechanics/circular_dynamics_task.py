"""CircularDynamicsTask — динамика движения по окружности (центростремительная сила).

Подтипы: центростремительная сила, максимальная скорость на повороте с трением,
минимальная скорость в верхней точке «мёртвой петли». Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class CircularDynamicsTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Центростремительная сила и связанные задачи."""

    TASK_TYPE = "circular_dynamics"
    TASK_TYPES = ["centripetal_force", "car_turn", "vertical_loop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 2, "max_v": 10, "max_r": 5}, 2: {"max_m": 5, "max_v": 15, "max_r": 10},
        3: {"max_m": 10, "max_v": 20, "max_r": 20}, 4: {"max_m": 20, "max_v": 25, "max_r": 30},
        5: {"max_m": 50, "max_v": 30, "max_r": 50}, 6: {"max_m": 100, "max_v": 40, "max_r": 80},
        7: {"max_m": 200, "max_v": 50, "max_r": 120}, 8: {"max_m": 500, "max_v": 60, "max_r": 200},
        9: {"max_m": 1000, "max_v": 80, "max_r": 300}, 10: {"max_m": 1500, "max_v": 100, "max_r": 500},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.g = get_constant("g")
        preset = self._interpolate_difficulty(difficulty)

        self.m = random.randint(1, preset["max_m"])
        self.v = random.randint(2, preset["max_v"])
        self.r = random.randint(2, preset["max_r"])
        self.mu = round(random.uniform(0.2, 0.9), 2)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["circular_dynamics"]["problem"][self.task_type][language]
        if self.task_type == "centripetal_force":
            return p.format(m=self.m, r=self.r, v=self.v)
        if self.task_type == "car_turn":
            return p.format(r=self.r, mu=self.mu)
        return p.format(r=self.r)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["circular_dynamics"]["steps"]
        if self.task_type == "centripetal_force":
            F = self.m * self.v ** 2 / self.r
            u = "Н" if self.language == "ru" else "N"
            self.solution_steps.append(steps["centripetal_formula"][self.language])
            self.solution_steps.append(f"F = {self.m}·{self.v}²/{self.r} = {fmt(F)} {u}")
            self.final_answer = f"F = {fmt(F)} {u}"
            self._answer_numbers = [F]
        elif self.task_type == "car_turn":
            v = math.sqrt(self.mu * self.g * self.r)
            u = "м/с" if self.language == "ru" else "m/s"
            self.solution_steps.append(steps["car_formula"][self.language])
            self.solution_steps.append(f"v = √({self.mu}·{self.g}·{self.r}) = {fmt(v)} {u}")
            self.final_answer = f"v = {fmt(v)} {u}"
            self._answer_numbers = [v]
        else:
            v = math.sqrt(self.g * self.r)
            u = "м/с" if self.language == "ru" else "m/s"
            self.solution_steps.append(steps["loop_formula"][self.language])
            self.solution_steps.append(f"v = √({self.g}·{self.r}) = {fmt(v)} {u}")
            self.final_answer = f"v = {fmt(v)} {u}"
            self._answer_numbers = [v]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
