"""ElasticityTask — упругие деформации: напряжение, деформация, модуль Юнга, удлинение.

Проверка числовая с относительным допуском.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class ElasticityTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Закон Гука для стержня: σ = F/A, ε = ΔL/L, E = σ/ε, ΔL = F·L/(A·E)."""

    TASK_TYPE = "elasticity"
    TASK_TYPES = ["stress", "strain", "young_modulus", "elongation"]

    # Модуль Юнга материалов, Па.
    MATERIALS = {
        "steel": {"E": 2.0e11, "ru": "сталь", "en": "steel"},
        "aluminum": {"E": 7.0e10, "ru": "алюминий", "en": "aluminum"},
        "copper": {"E": 1.1e11, "ru": "медь", "en": "copper"},
        "glass": {"E": 7.0e10, "ru": "стекло", "en": "glass"},
        "titanium": {"E": 1.1e11, "ru": "титан", "en": "titanium"},
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_F": 500, "max_A": 20, "max_L": 2},
        2: {"max_F": 1000, "max_A": 40, "max_L": 3},
        3: {"max_F": 2000, "max_A": 60, "max_L": 4},
        4: {"max_F": 5000, "max_A": 80, "max_L": 5},
        5: {"max_F": 10000, "max_A": 100, "max_L": 6},
        6: {"max_F": 20000, "max_A": 150, "max_L": 8},
        7: {"max_F": 40000, "max_A": 200, "max_L": 10},
        8: {"max_F": 80000, "max_A": 300, "max_L": 12},
        9: {"max_F": 150000, "max_A": 400, "max_L": 15},
        10: {"max_F": 300000, "max_A": 500, "max_L": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "stress":
            self.F = random.randint(50, preset["max_F"])
            self.A = round(random.uniform(1, preset["max_A"]), 2)  # мм²
        elif self.task_type == "strain":
            self.L = round(random.uniform(0.5, preset["max_L"]), 2)
            self.dL = round(random.uniform(0.1, 20), 2)  # мм
        elif self.task_type == "young_modulus":
            self.sigma = random.randint(1_000_000, 200_000_000)
            self.eps = round(random.uniform(1e-4, 5e-3), 6)
        else:  # elongation
            mat_key = random.choice(list(self.MATERIALS))
            self._mat = self.MATERIALS[mat_key]
            self.E = self._mat["E"]
            self.F = random.randint(100, preset["max_F"])
            self.A = round(random.uniform(2, preset["max_A"]), 2)  # мм²
            self.L = round(random.uniform(0.5, preset["max_L"]), 2)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["elasticity"]["problem"][self.task_type][language]
        if self.task_type == "stress":
            return p.format(A=self.A, F=self.F)
        if self.task_type == "strain":
            return p.format(L=self.L, dL=self.dL)
        if self.task_type == "young_modulus":
            return p.format(sigma=self.sigma, eps=self.eps)
        mat_name = self._mat["ru"] if language == "ru" else self._mat["en"]
        return p.format(mat=mat_name, L=self.L, A=self.A, F=self.F, E=fmt(self.E))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["elasticity"]["steps"]
        if self.task_type == "stress":
            A_m2 = self.A * 1e-6
            sigma = self.F / A_m2
            self.solution_steps.append(steps["stress_formula"][self.language])
            self.solution_steps.append(f"σ = {self.F}/{fmt(A_m2)} = {fmt(sigma)} Па")
            self.final_answer = f"σ = {fmt(sigma)} Па"
            self._answer_numbers = [sigma]
        elif self.task_type == "strain":
            eps = (self.dL * 1e-3) / self.L
            self.solution_steps.append(steps["strain_formula"][self.language])
            self.solution_steps.append(f"ε = {fmt(self.dL*1e-3)}/{self.L} = {fmt(eps)}")
            self.final_answer = f"ε = {fmt(eps)}"
            self._answer_numbers = [eps]
        elif self.task_type == "young_modulus":
            E = self.sigma / self.eps
            self.solution_steps.append(steps["young_formula"][self.language])
            self.solution_steps.append(f"E = {self.sigma}/{self.eps} = {fmt(E)} Па")
            self.final_answer = f"E = {fmt(E)} Па"
            self._answer_numbers = [E]
        else:  # elongation
            A_m2 = self.A * 1e-6
            dL = self.F * self.L / (A_m2 * self.E)
            self.solution_steps.append(steps["elongation_formula"][self.language])
            self.solution_steps.append(
                f"ΔL = {self.F}·{self.L}/({fmt(A_m2)}·{fmt(self.E)}) = {fmt(dL)} м")
            self.final_answer = f"ΔL = {fmt(dL)} м"
            self._answer_numbers = [dL]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
