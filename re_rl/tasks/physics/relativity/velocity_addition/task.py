"""VelocityAdditionTask — релятивистское сложение коллинеарных скоростей.

u = (v + u')/(1 + v·u'/c²). Скорости задаются в долях c, ответ — доля c.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class VelocityAdditionTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Релятивистское сложение скоростей."""

    TASK_TYPE = "velocity_addition"
    TASK_TYPES = ["collinear"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_beta": 0.4}, 2: {"max_beta": 0.5}, 3: {"max_beta": 0.6},
        4: {"max_beta": 0.7}, 5: {"max_beta": 0.8}, 6: {"max_beta": 0.85},
        7: {"max_beta": 0.9}, 8: {"max_beta": 0.95}, 9: {"max_beta": 0.98},
        10: {"max_beta": 0.99},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = "collinear"
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.v = round(random.uniform(0.1, preset["max_beta"]), 2)
        self.w = round(random.uniform(0.1, preset["max_beta"]), 2)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["velocity_addition"]["problem"][self.task_type][language]
        return p.format(v=self.v, w=self.w)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["velocity_addition"]["steps"]
        u = (self.v + self.w) / (1 + self.v * self.w)
        self.solution_steps.append(steps["add_formula"][self.language])
        self.solution_steps.append(
            f"u = ({self.v} + {self.w})/(1 + {self.v}·{self.w}) = {fmt(u)}·c")
        self.final_answer = f"{fmt(u)}·c"
        self._answer_numbers = [u]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
