"""Чтение круговой диаграммы (визуальная задача, matplotlib).

Подтипы:
- ``largest``  — у какой категории самый большой сектор;
- ``smallest`` — у какой категории самый маленький сектор.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import string
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U

_PIE_COLORS = ["#268bd2", "#dc322f", "#2aa198", "#b58900", "#6c71c4", "#859900", "#d33682"]


class PieChartReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = texts.literal('literals.s6')
    TASK_TYPES = ["largest", "smallest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n = int(p["n"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        self.labels = list(string.ascii_uppercase[:self.n])
        for _ in range(200):
            self.values = [random.randint(5, 30) for _ in range(self.n)]
            mx, mn = max(self.values), min(self.values)
            # уникальные максимум и минимум, различимые визуально
            if (self.values.count(mx) == 1 and self.values.count(mn) == 1
                    and mx - mn >= 4):
                break
        self.i_max = max(range(self.n), key=lambda i: self.values[i])
        self.i_min = min(range(self.n), key=lambda i: self.values[i])

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4.2, 4.2))
        ax.pie(self.values, labels=self.labels, colors=_PIE_COLORS[:self.n],
               startangle=90, wedgeprops={"edgecolor": "white"})
        ax.set_title(texts.t('s7', self.language))
        ax.set_aspect("equal")
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "largest":
            return ((texts.t('s3', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        idx = self.i_max if self.task_type == "largest" else self.i_min
        lbl = self.labels[idx]
        word = (texts.t('s1', self.language) if self.task_type == "largest" else texts.t('s2', self.language))
        self.solution_steps = [
            ((texts.t('s4', self.language, word=word))),
            ((texts.t('s5', self.language, lbl=lbl)))]
        self.final_answer = lbl
        self._label = lbl

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self._label])

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
