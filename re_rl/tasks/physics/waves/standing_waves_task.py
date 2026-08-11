"""StandingWavesTask — стоячие волны: гармоники струны и труб.

Подтипы: струна (закреплена с двух концов), открытая труба, закрытая труба
(только нечётные гармоники). Проверка числовая по частоте.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class StandingWavesTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Гармоники стоячих волн."""

    TASK_TYPE = "standing_waves"
    TASK_TYPES = ["string", "pipe_open", "pipe_closed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_n": 2, "max_L": 1}, 2: {"max_n": 3, "max_L": 1.5},
        3: {"max_n": 3, "max_L": 2}, 4: {"max_n": 4, "max_L": 2.5},
        5: {"max_n": 5, "max_L": 3}, 6: {"max_n": 6, "max_L": 4},
        7: {"max_n": 7, "max_L": 5}, 8: {"max_n": 8, "max_L": 6},
        9: {"max_n": 9, "max_L": 8}, 10: {"max_n": 10, "max_L": 10},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.L = round(random.uniform(0.5, preset["max_L"]), 2)
        # Скорость: для струны — произвольная, для труб — скорость звука.
        if self.task_type == "string":
            self.v = random.randint(50, 400)
        else:
            self.v = random.choice([330, 340, 343, 350])
        n = random.randint(1, preset["max_n"])
        if self.task_type == "pipe_closed":  # только нечётные гармоники
            n = 2 * n - 1
        self.n = n

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["standing_waves"]["problem"][self.task_type][language]
        return p.format(L=self.L, v=self.v, n=self.n)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["standing_waves"]["steps"]
        u = "Гц" if self.language == "ru" else "Hz"
        if self.task_type == "pipe_closed":
            f = self.n * self.v / (4 * self.L)
            self.solution_steps.append(steps["closed_formula"][self.language])
            self.solution_steps.append(f"f = {self.n}·{self.v}/(4·{self.L}) = {fmt(f)} {u}")
        else:
            key = "string_formula" if self.task_type == "string" else "open_formula"
            f = self.n * self.v / (2 * self.L)
            self.solution_steps.append(steps[key][self.language])
            self.solution_steps.append(f"f = {self.n}·{self.v}/(2·{self.L}) = {fmt(f)} {u}")
        self.final_answer = f"f = {fmt(f)} {u}"
        self._answer_numbers = [f]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
