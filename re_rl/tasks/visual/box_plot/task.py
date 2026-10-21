"""BoxPlotTask — чтение диаграммы размаха (ящик с усы).

Пять чисел стоят на делениях оси, в тексте их нет. Усы доходят до минимума
и максимума (выбросов нет), оранжевая черта — медиана.

Подтипы: ``median``, ``iqr`` (Q3 − Q1), ``range`` (max − min).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class BoxPlotTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "box_plot"
    TASK_TYPES = ["median", "iqr", "range"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"step": 1, "gap": 3}, 2: {"step": 1, "gap": 3}, 3: {"step": 1, "gap": 4},
        4: {"step": 1, "gap": 4}, 5: {"step": 2, "gap": 4}, 6: {"step": 2, "gap": 4},
        7: {"step": 2, "gap": 5}, 8: {"step": 5, "gap": 4}, 9: {"step": 5, "gap": 4},
        10: {"step": 5, "gap": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.step = int(p["step"])
        self.gap = int(p["gap"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        step = self.step
        x = random.randint(0, 2) * step
        vals = [x]
        for i in range(4):
            # ящик (между Q1 и Q3) не уже двух шагов
            lo = 2 if i == 2 else 1
            vals.append(vals[-1] + random.randint(lo, self.gap) * step)
        self.lo, self.q1, self.med, self.q3, self.hi = vals
        self.answer = {
            "median": self.med,
            "iqr": self.q3 - self.q1,
            "range": self.hi - self.lo,
        }[self.task_type]

    def render_image(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        fig, ax = plt.subplots(figsize=(7.4, 2.6))
        y = 0.0
        ax.plot([self.lo, self.q1], [y, y], color="#333", lw=1.6, zorder=2)
        ax.plot([self.q3, self.hi], [y, y], color="#333", lw=1.6, zorder=2)
        ax.plot([self.lo, self.lo], [-0.18, 0.18], color="#333", lw=1.6)
        ax.plot([self.hi, self.hi], [-0.18, 0.18], color="#333", lw=1.6)
        ax.add_patch(Rectangle((self.q1, -0.38), self.q3 - self.q1, 0.76,
                               facecolor="#e8f4fc", edgecolor="#333", lw=1.6, zorder=3))
        ax.plot([self.med, self.med], [-0.48, 0.48], color="#cb4b16", lw=2.6, zorder=4)
        pad = self.step
        ax.set_xlim(self.lo - pad, self.hi + pad)
        ax.set_ylim(-1.1, 1.0)
        ticks = list(range(self.lo, self.hi + 1, self.step))
        ax.set_xticks(ticks)
        ax.set_yticks([])
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(True, axis="x", linestyle=":", alpha=0.7)
        for spine in ("left", "right", "top"):
            ax.spines[spine].set_visible(False)
        return fig_to_image(fig)

    def _descr(self, language):
        asks = {
            "median": ((texts.t('s1', language))),
            "iqr": ((texts.t('s2', language))),
            "range": ((texts.t('s3', language))),
        }[self.task_type]
        head = (((texts.t('s0', language))))
        return f"{head} {asks}"

    def solve(self):
        note = {
            "median": ((texts.t('s4', self.language, med=self.med))),
            "iqr": ((texts.t('s5', self.language, q1=self.q1, q3=self.q3, answer=self.answer))),
            "range": ((texts.t('s6', self.language, lo=self.lo, hi=self.hi, answer=self.answer))),
        }[self.task_type]
        self.solution_steps = [note, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
