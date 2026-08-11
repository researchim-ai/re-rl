"""PairProductionTask — рождение электрон-позитронной пары гамма-квантом.

Проверка числовая с относительным допуском.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt
from re_rl.tasks.physics.constants import get_constant


class PairProductionTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Порог E = 2·m_e·c² ≈ 1.022 МэВ; λ = h/(2·m_e·c); KE = E − 2·m_e·c²."""

    TASK_TYPE = "pair_production"
    TASK_TYPES = ["threshold_energy", "threshold_wavelength", "excess_kinetic"]

    MEV_J = 1.602176634e-13  # 1 МэВ в джоулях

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_extra": 0.5}, 2: {"max_extra": 1.0}, 3: {"max_extra": 2.0},
        4: {"max_extra": 3.0}, 5: {"max_extra": 5.0}, 6: {"max_extra": 8.0},
        7: {"max_extra": 12.0}, 8: {"max_extra": 20.0}, 9: {"max_extra": 30.0},
        10: {"max_extra": 50.0},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "excess_kinetic":
            # Энергия кванта в МэВ, заведомо выше порога 1.022 МэВ.
            self.E = round(1.022 + random.uniform(0.05, preset["max_extra"]), 3)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["pair_production"]["problem"][self.task_type][language]
        if self.task_type == "excess_kinetic":
            return p.format(E=self.E)
        return p

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["pair_production"]["steps"]
        m_e = get_constant("m_e")
        c = get_constant("c")
        h = get_constant("h")
        threshold_J = 2 * m_e * c ** 2
        threshold_MeV = threshold_J / self.MEV_J

        if self.task_type == "threshold_energy":
            self.solution_steps.append(steps["threshold_formula"][self.language])
            self.solution_steps.append(
                f"E = 2·{fmt(m_e)}·{fmt(c)}² = {fmt(threshold_J)} Дж = {fmt(threshold_MeV)} МэВ")
            self.final_answer = f"E = {fmt(threshold_MeV)} МэВ"
            self._answer_numbers = [threshold_MeV]
        elif self.task_type == "threshold_wavelength":
            lam = h * c / threshold_J
            self.solution_steps.append(steps["wavelength_formula"][self.language])
            self.solution_steps.append(
                f"λ = {fmt(h)}·{fmt(c)}/{fmt(threshold_J)} = {fmt(lam)} м")
            self.final_answer = f"λ = {fmt(lam)} м"
            self._answer_numbers = [lam]
        else:  # excess_kinetic
            KE = self.E - threshold_MeV
            self.solution_steps.append(steps["excess_formula"][self.language])
            self.solution_steps.append(
                f"KE = {self.E} − {fmt(threshold_MeV)} = {fmt(KE)} МэВ")
            self.final_answer = f"KE = {fmt(KE)} МэВ"
            self._answer_numbers = [KE]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
