"""MeanFreePathTask — средняя длина свободного пробега, концентрация, частота столкновений.

Проверка числовая с относительным допуском.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class MeanFreePathTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """λ = k_B·T/(√2·π·d²·P); n = P/(k_B·T); z = v/λ."""

    TASK_TYPE = texts.literal('literals.s0')
    TASK_TYPES = [texts.literal('literals.s1'), "number_density", "collision_frequency"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_P": 101325, "max_T": 300}, 2: {"max_P": 200000, "max_T": 400},
        3: {"max_P": 300000, "max_T": 500}, 4: {"max_P": 500000, "max_T": 600},
        5: {"max_P": 1000000, "max_T": 700}, 6: {"max_P": 2000000, "max_T": 900},
        7: {"max_P": 5000000, "max_T": 1100}, 8: {"max_P": 10000000, "max_T": 1300},
        9: {"max_P": 20000000, "max_T": 1600}, 10: {"max_P": 50000000, "max_T": 2000},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == texts.t('s2', language):
            self.d = round(random.uniform(2.0, 5.0), 2) * 1e-10  # диаметр, м
            self.P = random.randint(1000, preset["max_P"])
            self.T = random.randint(200, preset["max_T"])
        elif self.task_type == "number_density":
            self.P = random.randint(1000, preset["max_P"])
            self.T = random.randint(200, preset["max_T"])
        else:  # collision_frequency
            self.v = random.randint(200, 2000)
            self.lam = round(random.uniform(1e-8, 1e-6), 10)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES[texts.t('s12', language)]["problem"][self.task_type][language]
        if self.task_type == texts.t('s3', language):
            return p.format(d=fmt(self.d), P=self.P, T=self.T)
        if self.task_type == "number_density":
            return p.format(P=self.P, T=self.T)
        return p.format(v=self.v, lam=fmt(self.lam))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES[texts.t('s6', self.language)]["steps"]
        kB = get_constant("k_B")
        if self.task_type == texts.t('s4', self.language):
            lam = kB * self.T / (math.sqrt(2) * math.pi * self.d ** 2 * self.P)
            self.solution_steps.append(steps["mfp_formula"][self.language])
            self.solution_steps.append(
                texts.t('s7', self.language, v0=fmt(kB), T=self.T, v2=fmt(self.d), P=self.P, v4=fmt(lam)))
            self.final_answer = texts.t('s5', self.language, v0=fmt(lam))
            self._answer_numbers = [lam]
        elif self.task_type == "number_density":
            n = self.P / (kB * self.T)
            self.solution_steps.append(steps["density_formula"][self.language])
            self.solution_steps.append(texts.t('s10', self.language, P=self.P, v1=fmt(kB), T=self.T, v3=fmt(n)))
            self.final_answer = texts.t('s8', self.language, v0=fmt(n))
            self._answer_numbers = [n]
        else:  # collision_frequency
            z = self.v / self.lam
            self.solution_steps.append(steps["frequency_formula"][self.language])
            self.solution_steps.append(texts.t('s11', self.language, v=self.v, v1=fmt(self.lam), v2=fmt(z)))
            self.final_answer = texts.t('s9', self.language, v0=fmt(z))
            self._answer_numbers = [z]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
