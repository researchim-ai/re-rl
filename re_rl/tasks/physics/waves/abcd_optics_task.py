"""ABCDOpticsTask — матричная (ABCD) оптика для последовательности элементов.

Масштабируется числом элементов N (тонкие линзы + свободные промежутки).
Проверка числовая (относительный допуск 2%).
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt

Matrix = List[List[float]]


def _matmul(a: Matrix, b: Matrix) -> Matrix:
    return [
        [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
        [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]],
    ]


class ABCDOpticsTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Матрица системы M = M_n·…·M_1; f = −1/C; изображение при B_total = 0."""

    TASK_TYPE = "abcd_optics"
    TASK_TYPES = ["effective_focal", "image_position", "magnification"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 5}, 7: {"n": 5}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        self.n_elements = max(2, int(round(preset["n"])))

        self.elements: List[Tuple[str, float]] = self._build_valid_system()
        if self.task_type in ("image_position", "magnification"):
            self.s = round(random.uniform(0.15, 1.2), 3)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build_elements(self) -> List[Tuple[str, float]]:
        elems: List[Tuple[str, float]] = []
        for _ in range(self.n_elements):
            if random.random() < 0.5:
                elems.append(("lens", round(random.uniform(0.05, 0.5), 3)))
            else:
                elems.append(("space", round(random.uniform(0.03, 0.4), 3)))
        if not any(e[0] == "lens" for e in elems):
            elems[random.randrange(len(elems))] = ("lens", round(random.uniform(0.05, 0.5), 3))
        return elems

    def _build_valid_system(self) -> List[Tuple[str, float]]:
        for _ in range(200):
            elems = self._build_elements()
            self.elements = elems
            M = self._system_matrix()
            if abs(M[1][0]) < 1e-9:  # нужен ненулевой C (есть оптическая сила)
                continue
            if self.task_type in ("image_position", "magnification"):
                # Проверяем разрешимость уравнения изображения для типичного s.
                s = 0.5
                t0 = _matmul(M, [[1, s], [0, 1]])
                if abs(t0[1][1]) < 1e-9:
                    continue
            return elems
        return elems  # запасной вариант

    @staticmethod
    def _elem_matrix(kind: str, val: float) -> Matrix:
        if kind == "space":
            return [[1.0, val], [0.0, 1.0]]
        return [[1.0, 0.0], [-1.0 / val, 1.0]]  # тонкая линза

    def _system_matrix(self) -> Matrix:
        M: Matrix = [[1.0, 0.0], [0.0, 1.0]]
        for kind, val in self.elements:  # по ходу луча: M = elem·M
            M = _matmul(self._elem_matrix(kind, val), M)
        return M

    def _render_elements(self, language: str) -> str:
        parts = []
        for kind, val in self.elements:
            if kind == "lens":
                parts.append(f"тонкая линза f={val} м" if language == "ru"
                             else f"thin lens f={val} m")
            else:
                parts.append(f"свободный промежуток d={val} м" if language == "ru"
                             else f"free space d={val} m")
        return "; ".join(parts)

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["abcd_optics"]["problem"][self.task_type][language]
        elems = self._render_elements(language)
        if self.task_type == "effective_focal":
            return p.format(elements=elems)
        return p.format(elements=elems, s=self.s)

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["abcd_optics"]["steps"]
        M = self._system_matrix()
        self.solution_steps.append(steps["matrices"][self.language])
        self.solution_steps.append(steps["product"][self.language])
        self.solution_steps.append(
            f"M = [[{fmt(M[0][0])}, {fmt(M[0][1])}], [{fmt(M[1][0])}, {fmt(M[1][1])}]]")

        if self.task_type == "effective_focal":
            f = -1.0 / M[1][0]
            self.solution_steps.append(steps["focal"][self.language])
            self.solution_steps.append(f"f = −1/({fmt(M[1][0])}) = {fmt(f)} м")
            self.final_answer = f"f = {fmt(f)} м"
            self._answer_numbers = [f]
        else:
            t0 = _matmul(M, [[1.0, self.s], [0.0, 1.0]])
            di = -t0[0][1] / t0[1][1]
            if self.task_type == "image_position":
                self.solution_steps.append(steps["image"][self.language])
                self.solution_steps.append(f"s' = {fmt(di)} м")
                self.final_answer = f"s' = {fmt(di)} м"
                self._answer_numbers = [di]
            else:  # magnification
                m = t0[0][0] + di * t0[1][0]
                self.solution_steps.append(steps["image"][self.language])
                self.solution_steps.append(steps["magnif"][self.language])
                self.solution_steps.append(f"m = {fmt(m)}")
                self.final_answer = f"m = {fmt(m)}"
                self._answer_numbers = [m]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
