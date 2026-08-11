"""BeatsTask — биения двух близких частот: f_beat = |f1 − f2|."""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class BeatsTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Частота биений."""

    TASK_TYPE = "beats"
    TASK_TYPES = ["beat_frequency"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"base": 256, "max_diff": 3}, 2: {"base": 300, "max_diff": 4},
        3: {"base": 350, "max_diff": 5}, 4: {"base": 400, "max_diff": 6},
        5: {"base": 440, "max_diff": 8}, 6: {"base": 500, "max_diff": 10},
        7: {"base": 600, "max_diff": 12}, 8: {"base": 700, "max_diff": 15},
        9: {"base": 800, "max_diff": 18}, 10: {"base": 1000, "max_diff": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = "beat_frequency"
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.f1 = preset["base"] + random.randint(-20, 20)
        diff = random.randint(1, preset["max_diff"])
        self.f2 = self.f1 + random.choice([-1, 1]) * diff

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["beats"]["problem"][self.task_type][language]
        return p.format(f1=self.f1, f2=self.f2)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["beats"]["steps"]
        f = abs(self.f1 - self.f2)
        u = "Гц" if self.language == "ru" else "Hz"
        self.solution_steps.append(steps["beat_formula"][self.language])
        self.solution_steps.append(f"f_биений = |{self.f1} − {self.f2}| = {f} {u}")
        self.final_answer = f"{fmt(float(f))} {u}"
        self._answer_numbers = [float(f)]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
