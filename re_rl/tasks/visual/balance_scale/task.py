"""BalanceScaleTask — неизвестная масса по рисунку равновесия.

Подтипы:
- ``equal_arm`` — чашечные весы, плечи равны: сумма слева равна сумме справа;
- ``lever``     — рычаг с опорой в 0: момент слева равен моменту справа.

Номиналы и расстояния подписаны на рисунке, в тексте их нет. Неизвестный груз — «?».
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class BalanceScaleTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "balance_scale"
    TASK_TYPES = ["equal_arm", "lever"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n_left": 1, "n_right": 0},
        2: {"n_left": 2, "n_right": 0},
        3: {"n_left": 2, "n_right": 0},
        4: {"n_left": 2, "n_right": 1},
        5: {"n_left": 2, "n_right": 1},
        6: {"n_left": 2, "n_right": 1},
        7: {"n_left": 3, "n_right": 1},
        8: {"n_left": 3, "n_right": 2},
        9: {"n_left": 3, "n_right": 2},
        10: {"n_left": 3, "n_right": 2},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_left = int(p["n_left"])
        self.n_right = int(p["n_right"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.task_type == "lever":
            self.d_l = random.randint(2, 5)
            self.d_r = random.randint(2, 5)
            k = random.randint(2, 8)
            self.m_l = k * self.d_r
            self.answer = k * self.d_l
            return
        self.left = [random.randint(1, 9) for _ in range(self.n_left)]
        self.right = [random.randint(1, 6) for _ in range(self.n_right)]
        if sum(self.right) >= sum(self.left):
            self.left.append(sum(self.right) - sum(self.left) + random.randint(1, 6))
        self.answer = sum(self.left) - sum(self.right)

    def _unit(self) -> str:
        return (texts.t('s0', self.language))

    def render_image(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch, Polygon

        if self.task_type == "lever":
            return self._render_lever(plt, FancyBboxPatch, Polygon)
        return self._render_pans(plt, FancyBboxPatch, Polygon)

    def _mass_box(self, ax, FancyBboxPatch, x, y, text, w=1.15, h=0.46):
        ax.add_patch(FancyBboxPatch((x - w / 2, y), w, h, boxstyle=texts.t('s6', self.language),
                                    facecolor="#fdf6e3", edgecolor="#333", lw=1.2, zorder=3))
        ax.text(x, y + h / 2, text, ha="center", va="center", fontsize=10, zorder=4)

    def _render_pans(self, plt, FancyBboxPatch, Polygon):
        unit = self._unit()
        left_labels = [f"{m} {unit}" for m in self.left]
        right_labels = [f"{m} {unit}" for m in self.right] + ["?"]
        nstack = max(len(left_labels), len(right_labels))
        gap = 0.54
        base = 0.2
        beam_y = base + nstack * gap + 0.85
        fig, ax = plt.subplots(figsize=(6.6, 1.8 + 0.55 * nstack))
        ax.plot([-3.4, 3.4], [beam_y, beam_y], color="#333", lw=3, solid_capstyle="round", zorder=2)
        ax.add_patch(Polygon(
            [[0, beam_y], [-0.28, beam_y - 0.42], [0.28, beam_y - 0.42]],
            closed=True, facecolor="#ccc", edgecolor="#333", zorder=2,
        ))
        for x, labels in ((-2.15, left_labels), (2.15, right_labels)):
            ax.plot([x - 0.78, x - 0.78], [base, beam_y], color="#333", lw=1.15, zorder=1)
            ax.plot([x + 0.78, x + 0.78], [base, beam_y], color="#333", lw=1.15, zorder=1)
            ax.plot([x - 0.95, x + 0.95], [base, base], color="#333", lw=2.4, zorder=2)
            for i, lab in enumerate(labels):
                self._mass_box(ax, FancyBboxPatch, x, base + 0.08 + i * gap, lab)
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-0.05, beam_y + 0.35)
        ax.set_aspect("equal")
        ax.axis("off")
        return fig_to_image(fig)

    def _render_lever(self, plt, FancyBboxPatch, Polygon):
        unit = self._unit()
        left, right = -self.d_l, self.d_r
        fig, ax = plt.subplots(figsize=(7.2, 3.6))
        ax.plot([left - 0.9, right + 0.9], [0, 0], color="#333", lw=3, solid_capstyle="round", zorder=2)
        ax.add_patch(Polygon([[0, 0], [-0.28, -0.42], [0.28, -0.42]], closed=True,
                             facecolor="#ccc", edgecolor="#333", zorder=2))
        ax.text(0, -0.5, "0", ha="center", va="top", fontsize=11)
        for pos, dist in ((left, self.d_l), (right, self.d_r)):
            ax.annotate(
                "", xy=(pos, -0.85), xytext=(0, -0.85),
                arrowprops=dict(arrowstyle="<->", color="#555", lw=1.1),
            )
            ax.text(pos / 2, -1.12, str(dist), ha="center", va="top", fontsize=12, color="#333")
        self._mass_box(ax, FancyBboxPatch, left, 0.18, f"{self.m_l} {unit}")
        self._mass_box(ax, FancyBboxPatch, right, 0.18, "?")
        ax.set_xlim(left - 1.4, right + 1.4)
        ax.set_ylim(-1.55, 1.15)
        ax.set_aspect("equal")
        ax.axis("off")
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "lever":
            return ((texts.t('s3', language)))
        return ((texts.t('s1', language)))

    def solve(self):
        unit = (texts.t('s2', self.language))
        if self.task_type == "lever":
            step = ((texts.t('s4', self.language, m_l=self.m_l, d_l=self.d_l, d_r=self.d_r, answer=self.answer, unit=unit)))
        else:
            step = ((texts.t('s5', self.language, v0=sum(self.left), v1=sum(self.right), answer=self.answer, unit=unit)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language="ru", detail_level=3,
                             difficulty=5, reasoning_mode=False, augment=True, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
