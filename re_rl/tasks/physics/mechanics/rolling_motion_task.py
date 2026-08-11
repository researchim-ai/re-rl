"""RollingMotionTask — качение без проскальзывания по наклонной плоскости.

Коэффициент k = I/(mR²) зависит от формы тела. Подтипы: ускорение центра масс,
скорость у основания, доля вращательной энергии. Проверка числовая.
"""

import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class RollingMotionTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Качение без проскальзывания (ускорение, скорость, доля энергии)."""

    TASK_TYPE = "rolling_motion"
    TASK_TYPES = ["incline_acceleration", "final_speed", "rotational_fraction"]

    # k = I/(mR²) для разных форм.
    SHAPES = {
        "hoop": {"k": 1.0, "ru": "обруч", "en": "hoop"},
        "disk": {"k": 0.5, "ru": "диск", "en": "disk"},
        "sphere": {"k": 0.4, "ru": "сплошной шар", "en": "solid sphere"},
        "shell": {"k": 2.0 / 3.0, "ru": "сферическая оболочка", "en": "spherical shell"},
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_angle": 20, "max_h": 2}, 2: {"max_angle": 25, "max_h": 3},
        3: {"max_angle": 30, "max_h": 4}, 4: {"max_angle": 35, "max_h": 5},
        5: {"max_angle": 40, "max_h": 6}, 6: {"max_angle": 45, "max_h": 8},
        7: {"max_angle": 50, "max_h": 10}, 8: {"max_angle": 55, "max_h": 12},
        9: {"max_angle": 60, "max_h": 15}, 10: {"max_angle": 65, "max_h": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        self.g = get_constant("g")
        preset = self._interpolate_difficulty(difficulty)

        self.shape_key = random.choice(list(self.SHAPES.keys()))
        self.k = self.SHAPES[self.shape_key]["k"]
        self.angle = random.randint(10, preset["max_angle"])
        self.h = random.randint(1, preset["max_h"])

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _shape_name(self, language: str) -> str:
        return self.SHAPES[self.shape_key][language]

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["rolling_motion"]["problem"][self.task_type][language]
        shape = self._shape_name(language)
        if self.task_type == "incline_acceleration":
            return p.format(shape=shape, angle=self.angle)
        if self.task_type == "final_speed":
            return p.format(shape=shape, h=self.h)
        return p.format(shape=shape)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["rolling_motion"]["steps"]
        if self.task_type == "incline_acceleration":
            a = self.g * math.sin(math.radians(self.angle)) / (1 + self.k)
            u = "м/с²" if self.language == "ru" else "m/s²"
            self.solution_steps.append(steps["accel_formula"][self.language])
            self.solution_steps.append(f"k = {self.k:.3f}; a = g·sin({self.angle}°)/(1+k) = {fmt(a)} {u}")
            self.final_answer = f"a = {fmt(a)} {u}"
            self._answer_numbers = [a]
        elif self.task_type == "final_speed":
            v = math.sqrt(2 * self.g * self.h / (1 + self.k))
            u = "м/с" if self.language == "ru" else "m/s"
            self.solution_steps.append(steps["speed_formula"][self.language])
            self.solution_steps.append(f"k = {self.k:.3f}; v = √(2·g·{self.h}/(1+k)) = {fmt(v)} {u}")
            self.final_answer = f"v = {fmt(v)} {u}"
            self._answer_numbers = [v]
        else:
            frac = self.k / (1 + self.k)
            self.solution_steps.append(steps["fraction_formula"][self.language])
            self.solution_steps.append(f"k = {self.k:.3f}; доля = k/(1+k) = {fmt(frac)}")
            self.final_answer = f"{fmt(frac)}"
            self._answer_numbers = [frac]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
