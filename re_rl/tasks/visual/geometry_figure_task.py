"""Геометрическая фигура (визуальная задача, matplotlib).

По изображению треугольника с подписанными величинами нужно найти:
- ``right_triangle_area`` — площадь прямоугольного треугольника по катетам;
- ``perimeter``          — периметр по трём подписанным сторонам;
- ``missing_angle``      — третий угол по двум подписанным.
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class GeometryFigureTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "geometry_figure"
    TASK_TYPES = ["right_triangle_area", "perimeter", "missing_angle"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max": 8}, 2: {"max": 10}, 3: {"max": 12}, 4: {"max": 15}, 5: {"max": 18},
        6: {"max": 20}, 7: {"max": 25}, 8: {"max": 30}, 9: {"max": 40}, 10: {"max": 50},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.M = int(p["max"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        if self.task_type == "right_triangle_area":
            self.a = random.randint(2, self.M)
            self.b = random.randint(2, self.M)
            self.answer = self.a * self.b / 2
        elif self.task_type == "perimeter":
            # три стороны, удовлетворяющие неравенству треугольника
            while True:
                s = sorted(random.randint(2, self.M) for _ in range(3))
                if s[0] + s[1] > s[2]:
                    break
            self.sides = s
            self.answer = sum(s)
        else:  # missing_angle
            self.alpha = random.randint(30, 80)
            self.beta = random.randint(30, 150 - self.alpha)
            self.answer = 180 - self.alpha - self.beta

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4.2, 4.0))
        ax.set_aspect("equal")
        ax.axis("off")
        if self.task_type == "right_triangle_area":
            a, b = self.a, self.b
            pts = [(0, 0), (a, 0), (0, b)]
            tri = plt.Polygon(pts, fill=False, edgecolor="#268bd2", linewidth=2)
            ax.add_patch(tri)
            ax.plot([0.8, 0.8, 0], [0, 0.8, 0.8], color="black", linewidth=1)  # прямой угол
            ax.text(a / 2, -0.06 * b - 0.3, f"a = {a}", ha="center", va="top")
            ax.text(-0.06 * a - 0.3, b / 2, f"b = {b}", ha="right", va="center", rotation=90)
            ax.set_xlim(-0.2 * a - 1, a + 1)
            ax.set_ylim(-0.2 * b - 1, b + 1)
            ax.set_title("Прямоугольный треугольник")
        elif self.task_type == "perimeter":
            pts = [(0, 0), (4, 0), (1.4, 3)]
            tri = plt.Polygon(pts, fill=False, edgecolor="#2aa198", linewidth=2)
            ax.add_patch(tri)
            labels = self.sides
            ax.text(2, -0.35, str(labels[0]), ha="center", va="top")
            ax.text(2.9, 1.6, str(labels[1]), ha="left", va="center")
            ax.text(0.5, 1.6, str(labels[2]), ha="right", va="center")
            ax.set_xlim(-1, 5)
            ax.set_ylim(-1, 4)
            ax.set_title("Треугольник (стороны подписаны)")
        else:  # missing_angle
            pts = [(0, 0), (5, 0), (1.8, 3)]
            tri = plt.Polygon(pts, fill=False, edgecolor="#b58900", linewidth=2)
            ax.add_patch(tri)
            ax.text(0.35, 0.12, f"{self.alpha}°", ha="left", va="bottom")
            ax.text(4.4, 0.12, f"{self.beta}°", ha="right", va="bottom")
            ax.text(1.8, 2.7, "?", ha="center", va="top", fontsize=14)
            ax.set_xlim(-1, 6)
            ax.set_ylim(-1, 4)
            ax.set_title("Найдите неизвестный угол")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "right_triangle_area":
            return ("На рисунке — прямоугольный треугольник с подписанными катетами a и b. "
                    "Найдите его площадь." if ru else
                    "The figure shows a right triangle with legs a and b labeled. Find its area.")
        if self.task_type == "perimeter":
            return ("На рисунке — треугольник с подписанными длинами трёх сторон. Найдите его "
                    "периметр." if ru else
                    "The figure shows a triangle with all three side lengths labeled. Find its "
                    "perimeter.")
        return ("На рисунке — треугольник с двумя подписанными углами (в градусах). Найдите "
                "величину третьего угла." if ru else
                "The figure shows a triangle with two angles labeled (degrees). Find the third "
                "angle.")

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "right_triangle_area":
            self.solution_steps = [
                ("Площадь прямоугольного треугольника S = a·b/2." if ru else
                 "Right-triangle area S = a·b/2."),
                (f"S = {self.a}·{self.b}/2 = {self.answer:g}." if ru else
                 f"S = {self.a}·{self.b}/2 = {self.answer:g}.")]
        elif self.task_type == "perimeter":
            self.solution_steps = [
                ("Периметр — сумма длин сторон." if ru else "Perimeter is the sum of the sides."),
                (f"P = {' + '.join(map(str, self.sides))} = {self.answer}." if ru else
                 f"P = {' + '.join(map(str, self.sides))} = {self.answer}.")]
        else:
            self.solution_steps = [
                ("Сумма углов треугольника равна 180°." if ru else
                 "The angles of a triangle sum to 180°."),
                (f"γ = 180 − {self.alpha} − {self.beta} = {self.answer}°." if ru else
                 f"γ = 180 − {self.alpha} − {self.beta} = {self.answer}°.")]
        self.final_answer = f"{self.answer:g}"

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "right_triangle_area":
            return U.verify_value(prediction, float(self.answer), tol=1e-2)
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
