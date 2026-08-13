"""PVCycleTask — работа газа по PV-диаграмме (площадь замкнутого цикла).

Масштабируется числом вершин цикла. Проверка числовая (относительный допуск 2%).
"""

import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt


class PVCycleTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Работа газа = ∮P dV: площадь цикла (net_work) или работа по отрезку (leg_work)."""

    TASK_TYPE = "pv_cycle"
    TASK_TYPES = ["net_work", "leg_work"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"verts": 3, "max_P": 200000, "max_V": 0.05},
        2: {"verts": 3, "max_P": 300000, "max_V": 0.06},
        3: {"verts": 4, "max_P": 400000, "max_V": 0.08},
        4: {"verts": 4, "max_P": 500000, "max_V": 0.1},
        5: {"verts": 5, "max_P": 600000, "max_V": 0.12},
        6: {"verts": 6, "max_P": 800000, "max_V": 0.15},
        7: {"verts": 6, "max_P": 1000000, "max_V": 0.2},
        8: {"verts": 7, "max_P": 1500000, "max_V": 0.25},
        9: {"verts": 8, "max_P": 2000000, "max_V": 0.3},
        10: {"verts": 9, "max_P": 3000000, "max_V": 0.4},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset

        if self.task_type == "net_work":
            self.points = self._make_polygon(max(3, int(round(preset["verts"]))),
                                             preset["max_V"], int(preset["max_P"]))
        else:  # leg_work
            self.V1 = round(random.uniform(0.005, preset["max_V"]), 4)
            self.V2 = round(random.uniform(0.005, preset["max_V"]), 4)
            while abs(self.V2 - self.V1) < 0.005:
                self.V2 = round(random.uniform(0.005, preset["max_V"]), 4)
            self.P1 = random.randint(50000, int(preset["max_P"]))
            self.P2 = random.randint(50000, int(preset["max_P"]))

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _make_polygon(self, k: int, max_V: float, max_P: int) -> List[Tuple[float, int]]:
        """k вершин, отсортированных по углу вокруг центроида (простой многоугольник)."""
        pts = []
        for _ in range(k):
            pts.append((round(random.uniform(0.005, max_V), 4),
                        random.randint(50000, max_P)))
        # Уникализируем V, чтобы избежать вертикальных совпадений.
        cx = sum(p[0] for p in pts) / k
        cy = sum(p[1] for p in pts) / k
        pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        return pts

    def _cycle_work(self) -> float:
        pts = self.points
        n = len(pts)
        w = 0.0
        for i in range(n):
            v1, p1 = pts[i]
            v2, p2 = pts[(i + 1) % n]
            w += (p1 + p2) / 2.0 * (v2 - v1)
        return w

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["pv_cycle"]["problem"][self.task_type][language]
        if self.task_type == "net_work":
            pts_str = ", ".join(f"({v}, {P})" for v, P in self.points)
            return p.format(points=pts_str)
        return p.format(V1=self.V1, P1=self.P1, V2=self.V2, P2=self.P2)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["pv_cycle"]["steps"]
        if self.task_type == "net_work":
            W = self._cycle_work()
            self.solution_steps.append(steps["area_formula"][self.language])
            self.solution_steps.append(steps["trapezoid_formula"][self.language])
            self.solution_steps.append(steps["shoelace"][self.language])
            self.solution_steps.append(f"W = {fmt(W)} Дж")
            self.final_answer = f"W = {fmt(W)} Дж"
            self._answer_numbers = [W]
        else:  # leg_work
            W = (self.P1 + self.P2) / 2.0 * (self.V2 - self.V1)
            self.solution_steps.append(steps["trapezoid_formula"][self.language])
            self.solution_steps.append(
                f"W = ({self.P1}+{self.P2})/2·({self.V2}−{self.V1}) = {fmt(W)} Дж")
            self.final_answer = f"W = {fmt(W)} Дж"
            self._answer_numbers = [W]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
