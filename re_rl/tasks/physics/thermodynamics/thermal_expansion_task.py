"""ThermalExpansionTask — тепловое расширение (линейное и объёмное).

Проверка числовая по величине изменения размера/объёма.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class ThermalExpansionTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Тепловое расширение тел."""

    TASK_TYPE = "thermal_expansion"
    TASK_TYPES = ["linear", "volume"]

    # Коэффициенты линейного расширения α, 1/К.
    MATERIALS = {
        "steel": {"alpha": 12e-6, "ru": "сталь", "en": "steel"},
        "aluminum": {"alpha": 23e-6, "ru": "алюминий", "en": "aluminum"},
        "copper": {"alpha": 17e-6, "ru": "медь", "en": "copper"},
        "glass": {"alpha": 9e-6, "ru": "стекло", "en": "glass"},
        "brass": {"alpha": 19e-6, "ru": "латунь", "en": "brass"},
    }

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_L": 2, "max_dT": 50}, 2: {"max_L": 3, "max_dT": 80},
        3: {"max_L": 5, "max_dT": 100}, 4: {"max_L": 8, "max_dT": 150},
        5: {"max_L": 10, "max_dT": 200}, 6: {"max_L": 15, "max_dT": 250},
        7: {"max_L": 20, "max_dT": 300}, 8: {"max_L": 30, "max_dT": 400},
        9: {"max_L": 50, "max_dT": 500}, 10: {"max_L": 80, "max_dT": 600},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)

        self.material_key = random.choice(list(self.MATERIALS.keys()))
        self.alpha = self.MATERIALS[self.material_key]["alpha"]
        self.dT = random.randint(20, preset["max_dT"])
        self.L = round(random.uniform(0.5, preset["max_L"]), 2)
        self.V = round(random.uniform(0.01, max(0.02, preset["max_L"] / 10)), 3)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["thermal_expansion"]["problem"][self.task_type][language]
        material = self.MATERIALS[self.material_key][language]
        if self.task_type == "linear":
            return p.format(material=material, alpha=self.alpha, L=self.L, dT=self.dT)
        return p.format(material=material, alpha=self.alpha, V=self.V, dT=self.dT)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["thermal_expansion"]["steps"]
        if self.task_type == "linear":
            dL = self.alpha * self.L * self.dT
            u = "м" if self.language == "ru" else "m"
            self.solution_steps.append(steps["linear_formula"][self.language])
            self.solution_steps.append(f"ΔL = {self.alpha:.1e}·{self.L}·{self.dT} = {fmt(dL)} {u}")
            self.final_answer = f"ΔL = {fmt(dL)} {u}"
            self._answer_numbers = [dL]
        else:
            dV = 3 * self.alpha * self.V * self.dT
            u = "м³" if self.language == "ru" else "m³"
            self.solution_steps.append(steps["volume_formula"][self.language])
            self.solution_steps.append(f"ΔV = 3·{self.alpha:.1e}·{self.V}·{self.dT} = {fmt(dV)} {u}")
            self.final_answer = f"ΔV = {fmt(dV)} {u}"
            self._answer_numbers = [dV]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
