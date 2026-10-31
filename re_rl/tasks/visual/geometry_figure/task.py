"""Геометрическая фигура (визуальная задача, matplotlib).

По изображению треугольника с подписанными величинами нужно найти:
- ``right_triangle_area`` — площадь прямоугольного треугольника по катетам;
- ``perimeter``          — периметр по трём подписанным сторонам;
- ``missing_angle``      — третий угол по двум подписанным.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class GeometryFigureTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "geometry_figure"
    TASK_TYPES = [texts.literal('literals.s7'), "perimeter", "missing_angle"]

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
        if self.task_type == texts.t('s8', self.language):
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
        if self.task_type == texts.t('s9', self.language):
            a, b = self.a, self.b
            pts = [(0, 0), (a, 0), (0, b)]
            tri = plt.Polygon(pts, fill=False, edgecolor="#268bd2", linewidth=2)
            ax.add_patch(tri)
            ax.plot([0.8, 0.8, 0], [0, 0.8, 0.8], color="black", linewidth=1)  # прямой угол
            ax.text(a / 2, -0.06 * b - 0.3, f"a = {a}", ha="center", va="top")
            ax.text(-0.06 * a - 0.3, b / 2, f"b = {b}", ha="right", va="center", rotation=90)
            ax.set_xlim(-0.2 * a - 1, a + 1)
            ax.set_ylim(-0.2 * b - 1, b + 1)
            ax.set_title(texts.t('s13', self.language))
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
            ax.set_title(texts.t('s14', self.language))
        else:  # missing_angle
            pts = [(0, 0), (5, 0), (1.8, 3)]
            tri = plt.Polygon(pts, fill=False, edgecolor="#b58900", linewidth=2)
            ax.add_patch(tri)
            ax.text(0.35, 0.12, f"{self.alpha}°", ha="left", va="bottom")
            ax.text(4.4, 0.12, f"{self.beta}°", ha="right", va="bottom")
            ax.text(1.8, 2.7, "?", ha="center", va="top", fontsize=14)
            ax.set_xlim(-1, 6)
            ax.set_ylim(-1, 4)
            ax.set_title(texts.t('s15', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == texts.t('s10', language):
            return ((texts.t('s1', language)))
        if self.task_type == "perimeter":
            return ((texts.t('s2', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == texts.t('s11', self.language):
            self.solution_steps = [
                ((texts.t('s3', self.language))),
                ((f"S = {self.a}·{self.b}/2 = {self.answer:g}."))]
        elif self.task_type == "perimeter":
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((f"P = {' + '.join(map(str, self.sides))} = {self.answer}."))]
        else:
            self.solution_steps = [
                ((texts.t('s5', self.language))),
                ((texts.t('s6', self.language, alpha=self.alpha, beta=self.beta, answer=self.answer)))]
        self.final_answer = f"{self.answer:g}"

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == texts.t('s12', self.language):
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
