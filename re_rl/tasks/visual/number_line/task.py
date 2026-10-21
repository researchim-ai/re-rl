"""NumberLineTask — чтение числовой прямой.

Подтипы:
- ``value``    — целое, отмеченное одной точкой;
- ``distance`` — расстояние между точками A и B;
- ``midpoint`` — координата середины AB (точки одной чётности, середина целая).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class NumberLineTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "number_line"
    TASK_TYPES = ["value", "distance", "midpoint"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"lo": 0, "hi": 8}, 2: {"lo": 0, "hi": 8}, 3: {"lo": 0, "hi": 10},
        4: {"lo": 0, "hi": 12}, 5: {"lo": 0, "hi": 14}, 6: {"lo": 0, "hi": 14},
        7: {"lo": -4, "hi": 12}, 8: {"lo": -6, "hi": 12}, 9: {"lo": -8, "hi": 12},
        10: {"lo": -8, "hi": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.lo = int(p["lo"])
        self.hi = int(p["hi"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.task_type == "value":
            self.a = random.randint(self.lo, self.hi)
            self.b = None
            self.answer = self.a
            return
        if self.task_type == "midpoint":
            pool = [x for x in range(self.lo, self.hi + 1)]
            self.a = random.choice(pool)
            same = [x for x in pool if x != self.a and (x - self.a) % 2 == 0]
            self.b = random.choice(same)
        else:
            self.a = random.randint(self.lo, self.hi - 1)
            self.b = random.randint(self.a + 1, self.hi)
        if self.a > self.b:
            self.a, self.b = self.b, self.a
        self.answer = abs(self.b - self.a) if self.task_type == "distance" else (self.a + self.b) // 2

    def render_image(self):
        import matplotlib.pyplot as plt

        span = self.hi - self.lo
        fig, ax = plt.subplots(figsize=(max(5.4, span * 0.55 + 1.4), 2.4))
        ax.plot([self.lo, self.hi], [0, 0], color="#333", lw=1.4)
        for x in range(self.lo, self.hi + 1):
            ax.plot([x, x], [-0.08, 0.08], color="#333", lw=1)
        ax.set_xlim(self.lo - 0.6, self.hi + 0.6)
        ax.set_ylim(-0.95, 0.9)
        ticks = list(range(self.lo, self.hi + 1))
        ax.set_xticks(ticks)
        ax.set_yticks([])
        labels = ax.set_xticklabels([str(v) for v in ticks])
        marked = {self.a: "#cb4b16"}
        if self.b is not None:
            marked[self.b] = "#268bd2"
        for lab, v in zip(labels, ticks):
            if v in marked:
                lab.set_color(marked[v])
                lab.set_fontweight("bold")
                lab.set_fontsize(11)
            else:
                lab.set_fontsize(8)
        for spine in ("left", "right", "top"):
            ax.spines[spine].set_visible(False)
        if self.task_type == "value":
            self._pointer(ax, self.a, "#cb4b16", None, above=True)
        else:
            close = abs(self.a - self.b) <= 2
            self._pointer(ax, self.a, "#cb4b16", "A", above=True)
            self._pointer(ax, self.b, "#268bd2", "B", above=not close)
        return fig_to_image(fig)

    @staticmethod
    def _pointer(ax, x, color, label, above=True):
        """Стрелка, остриё которой стоит ровно на делении x."""
        y_text = 0.55 if above else -0.62
        ax.annotate(
            label or "",
            xy=(x, 0), xytext=(x, y_text),
            ha="center", va="bottom" if above else "top",
            fontsize=12, color=color, fontweight="bold",
            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4, mutation_scale=12),
            zorder=4,
        )
        ax.plot([x, x], [-0.14, 0.14], color=color, lw=2.6, zorder=3)

    def _descr(self, language):
        if self.task_type == "value":
            return ((texts.t('s1', language)))
        if self.task_type == "distance":
            return ((texts.t('s2', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        if self.task_type == "value":
            step = ((texts.t('s3', self.language, a=self.a)))
        elif self.task_type == "distance":
            step = ((f"|{self.b} - {self.a}| = {self.answer}."))
        else:
            step = ((texts.t('s4', self.language, a=self.a, b=self.b, answer=self.answer)))
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
