"""ElasticChainTask — цепочка одномерных упругих соударений (масштаб по числу шаров).

Классическая задача о передаче скорости через цепочку промежуточных масс. Массы
убывают, поэтому повторных соударений нет. Проверка числовая (относительный
допуск 2%).
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class ElasticChainTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """v_k = v₀·Π 2·m_{i−1}/(m_{i−1}+m_i) для лобовых упругих ударов."""

    TASK_TYPE = "elastic_chain"
    TASK_TYPES = ["last_velocity", "ball_velocity"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "max_v": 10}, 2: {"n": 2, "max_v": 15},
        3: {"n": 3, "max_v": 20}, 4: {"n": 3, "max_v": 25},
        5: {"n": 4, "max_v": 30}, 6: {"n": 5, "max_v": 40},
        7: {"n": 6, "max_v": 50}, 8: {"n": 7, "max_v": 60},
        9: {"n": 8, "max_v": 80}, 10: {"n": 10, "max_v": 100},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        n = max(2, int(round(preset["n"])))

        self.m0 = round(random.uniform(2.0, 6.0), 2)
        # Убывающие массы промежуточных шаров.
        self.masses: List[float] = []
        cur = self.m0
        for _ in range(n):
            cur = round(cur * random.uniform(0.5, 0.85), 3)
            self.masses.append(max(cur, 0.01))
        self.v0 = round(random.uniform(1.0, preset["max_v"]), 2)
        if self.task_type == "ball_velocity":
            self.k = random.randint(1, len(self.masses))

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _velocity_of(self, k: int) -> float:
        """Скорость k-го ударенного шара (1..N)."""
        v = self.v0
        prev = self.m0
        for i in range(k):
            m = self.masses[i]
            v = 2 * prev / (prev + m) * v
            prev = m
        return v

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["elastic_chain"]["problem"][self.task_type][language]
        masses_str = ", ".join(str(m) for m in self.masses)
        if self.task_type == "last_velocity":
            return p.format(m0=self.m0, v0=self.v0, masses=masses_str)
        return p.format(m0=self.m0, v0=self.v0, masses=masses_str, k=self.k)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["elastic_chain"]["steps"]
        self.solution_steps.append(steps["elastic_formula"][self.language])
        self.solution_steps.append(steps["chain_formula"][self.language])
        k = len(self.masses) if self.task_type == "last_velocity" else self.k
        v = self._velocity_of(k)
        self.solution_steps.append(f"v = {fmt(v)} м/с")
        self.final_answer = f"v = {fmt(v)} м/с"
        self._answer_numbers = [v]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
