"""CompositeInertiaTask — момент инерции составного тела (масштаб по числу частей).

Подтипы: точечные массы (I = Σ m·r²) и теорема Штейнера (I = Σ(I_cm + m·d²)).
Проверка числовая (относительный допуск 2%).
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class CompositeInertiaTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """I = Σ m_i·r_i² (точечные массы) или I = Σ(I_cm,i + m_i·d_i²) (Штейнер)."""

    TASK_TYPE = "composite_inertia"
    TASK_TYPES = ["point_masses", "parallel_axis_shapes"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "max_m": 5, "max_r": 2}, 2: {"n": 3, "max_m": 5, "max_r": 2},
        3: {"n": 3, "max_m": 8, "max_r": 3}, 4: {"n": 4, "max_m": 10, "max_r": 3},
        5: {"n": 5, "max_m": 12, "max_r": 4}, 6: {"n": 6, "max_m": 15, "max_r": 5},
        7: {"n": 7, "max_m": 20, "max_r": 5}, 8: {"n": 8, "max_m": 25, "max_r": 6},
        9: {"n": 9, "max_m": 30, "max_r": 8}, 10: {"n": 11, "max_m": 40, "max_r": 10},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        n = max(2, int(round(preset["n"])))

        if self.task_type == "point_masses":
            self.pairs: List[Tuple[float, float]] = [
                (round(random.uniform(0.5, preset["max_m"]), 2),
                 round(random.uniform(0.2, preset["max_r"]), 2)) for _ in range(n)]
        else:  # parallel_axis_shapes
            self.rows: List[Tuple[float, float, float]] = [
                (round(random.uniform(0.05, 2.0), 3),
                 round(random.uniform(0.5, preset["max_m"]), 2),
                 round(random.uniform(0.2, preset["max_r"]), 2)) for _ in range(n)]

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["composite_inertia"]["problem"][self.task_type][language]
        if self.task_type == "point_masses":
            s = ", ".join(f"({m}, {r})" for m, r in self.pairs)
            return p.format(pairs=s)
        s = ", ".join(f"(I_cm={icm}, m={m}, d={d})" for icm, m, d in self.rows)
        return p.format(rows=s)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["composite_inertia"]["steps"]
        if self.task_type == "point_masses":
            I = sum(m * r ** 2 for m, r in self.pairs)
            self.solution_steps.append(steps["point_formula"][self.language])
            self.solution_steps.append(
                "I = " + " + ".join(f"{m}·{r}²" for m, r in self.pairs) + f" = {fmt(I)} кг·м²")
        else:
            I = sum(icm + m * d ** 2 for icm, m, d in self.rows)
            self.solution_steps.append(steps["steiner_formula"][self.language])
            self.solution_steps.append(
                "I = " + " + ".join(f"({icm}+{m}·{d}²)" for icm, m, d in self.rows)
                + f" = {fmt(I)} кг·м²")
        self.final_answer = f"I = {fmt(I)} кг·м²"
        self._answer_numbers = [I]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
