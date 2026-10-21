"""Чтение гистограммы (визуальная задача, matplotlib).

Гистограмма показывает, сколько раз встречается каждое значение (1..K). По ней
нужно найти статистику набора данных.

Подтипы:
- ``mode``   — значение, встречающееся чаще всего;
- ``median`` — медиана набора;
- ``range``  — размах (макс. значение − мин. значение среди присутствующих).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class StatsHistogramTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "stats_histogram"
    TASK_TYPES = ["mode", "median", "range"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 4, "cmax": 4}, 2: {"k": 4, "cmax": 5}, 3: {"k": 5, "cmax": 5},
        4: {"k": 5, "cmax": 6}, 5: {"k": 6, "cmax": 6}, 6: {"k": 6, "cmax": 7},
        7: {"k": 7, "cmax": 7}, 8: {"k": 8, "cmax": 8}, 9: {"k": 9, "cmax": 8},
        10: {"k": 10, "cmax": 9},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.k = int(p["k"])
        self.cmax = int(p["cmax"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        for _ in range(200):
            self.counts = [random.randint(0, self.cmax) for _ in range(self.k)]
            if sum(self.counts) < 3:
                continue
            mx = max(self.counts)
            if self.counts.count(mx) == 1:  # уникальная мода
                break
        self.values = [i + 1 for i in range(self.k)]
        data = []
        for i, c in enumerate(self.counts):
            data += [i + 1] * c
        data.sort()
        self.data = data
        self.mode = self.counts.index(max(self.counts)) + 1
        present = [v for v, c in zip(self.values, self.counts) if c > 0]
        self.range_ = max(present) - min(present)
        n = len(data)
        self.median = data[n // 2] if n % 2 == 1 else (data[n // 2 - 1] + data[n // 2]) / 2.0
        self.answer = {"mode": self.mode, "median": self.median, "range": self.range_}[self.task_type]

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
        ax.bar(self.values, self.counts, color="#268bd2", edgecolor="#333333")
        ax.set_xticks(self.values)
        ax.set_yticks(range(0, self.cmax + 2))
        ax.set_xlabel(texts.t('s5', self.language))
        ax.set_ylabel(texts.t('s6', self.language))
        ax.grid(True, axis="y", linestyle=":", alpha=0.6)
        ax.set_title(texts.t('s7', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        q = {
            "mode": ((texts.t('s2', language))),
            "median": ((texts.t('s3', language))),
            "range": ((texts.t('s4', language))),
        }[self.task_type]
        head = ((texts.t('s0', language)))
        return head + q

    def solve(self):
        a = self.answer
        a_str = f"{a:g}" if isinstance(a, float) else str(a)
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.common('answer_line', self.language, answer=a_str)))]
        self.final_answer = a_str

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "median":
            return U.verify_value(prediction, float(self.median), tol=1e-3)
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
