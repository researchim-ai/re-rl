"""WheatstoneBridgeTask — мост Уитстона: баланс и напряжение разбаланса.

Проверка числовая с относительным допуском.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class WheatstoneBridgeTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Rx = R2·R3/R1; U_out = U·(R2/(R1+R2) − R4/(R3+R4))."""

    TASK_TYPE = "wheatstone_bridge"
    TASK_TYPES = ["unknown_resistance", "output_voltage"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_R": 100, "max_U": 5}, 2: {"max_R": 200, "max_U": 9},
        3: {"max_R": 500, "max_U": 12}, 4: {"max_R": 1000, "max_U": 24},
        5: {"max_R": 2000, "max_U": 30}, 6: {"max_R": 5000, "max_U": 48},
        7: {"max_R": 10000, "max_U": 60}, 8: {"max_R": 20000, "max_U": 100},
        9: {"max_R": 50000, "max_U": 150}, 10: {"max_R": 100000, "max_U": 220},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        mx = preset["max_R"]

        self.R1 = random.randint(10, mx)
        self.R2 = random.randint(10, mx)
        self.R3 = random.randint(10, mx)
        if self.task_type == "output_voltage":
            self.R4 = random.randint(10, mx)
            self.U = random.randint(2, preset["max_U"])

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["wheatstone_bridge"]["problem"][self.task_type][language]
        if self.task_type == "unknown_resistance":
            return p.format(R1=self.R1, R2=self.R2, R3=self.R3)
        return p.format(U=self.U, R1=self.R1, R2=self.R2, R3=self.R3, R4=self.R4)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["wheatstone_bridge"]["steps"]
        if self.task_type == "unknown_resistance":
            Rx = self.R2 * self.R3 / self.R1
            self.solution_steps.append(steps["balance_formula"][self.language])
            self.solution_steps.append(
                texts.t('s2', self.language, R2=self.R2, R3=self.R3, R1=self.R1, v3=fmt(Rx)))
            self.final_answer = texts.t('s0', self.language, v0=fmt(Rx))
            self._answer_numbers = [Rx]
        else:  # output_voltage
            Uout = self.U * (self.R2 / (self.R1 + self.R2) - self.R4 / (self.R3 + self.R4))
            self.solution_steps.append(steps["output_formula"][self.language])
            self.solution_steps.append(
                texts.t('s3', self.language, U=self.U, R2=self.R2, v2=self.R1 + self.R2, R4=self.R4, v4=self.R3 + self.R4, v5=fmt(Uout)))
            self.final_answer = texts.t('s1', self.language, v0=fmt(Uout))
            self._answer_numbers = [Uout]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
