"""Чтение линейного графика (визуальная задача, matplotlib).

Подтипы:
- ``value_at``      — значение y в отмеченной точке x;
- ``max_x``         — при каком x достигается максимум;
- ``num_increases`` — на скольких шагах значение возрастает.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class LinePlotReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = texts.literal('literals.s8')
    TASK_TYPES = ["value_at", "max_x", "num_increases"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "max_v": 8}, 2: {"n": 5, "max_v": 10}, 3: {"n": 6, "max_v": 10},
        4: {"n": 6, "max_v": 12}, 5: {"n": 7, "max_v": 12}, 6: {"n": 7, "max_v": 15},
        7: {"n": 8, "max_v": 15}, 8: {"n": 9, "max_v": 18}, 9: {"n": 10, "max_v": 20},
        10: {"n": 11, "max_v": 20},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n = int(p["n"])
        self.max_v = int(p["max_v"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        for _ in range(200):
            self.ys = [random.randint(0, self.max_v) for _ in range(self.n)]
            if self.ys.count(max(self.ys)) == 1:  # уникальный максимум
                break
        self.xs = list(range(self.n))
        if self.task_type == "value_at":
            self.k = random.randint(0, self.n - 1)
            self.answer = self.ys[self.k]
        elif self.task_type == "max_x":
            self.answer = max(self.xs, key=lambda i: self.ys[i])
        else:
            self.answer = sum(1 for i in range(1, self.n) if self.ys[i] > self.ys[i - 1])

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.0, 3.6))
        ax.plot(self.xs, self.ys, marker="o", color="#268bd2", linewidth=2)
        if self.task_type == "value_at":
            ax.axvline(self.k, color="#dc322f", linestyle="--", linewidth=1)
        ax.set_xticks(self.xs)
        ax.set_yticks(range(0, self.max_v + 2))
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(texts.t('s9', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "value_at":
            return ((texts.t('s1', language, k=self.k)))
        if self.task_type == "max_x":
            return ((texts.t('s2', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        if self.task_type == "value_at":
            steps = [((texts.t('s3', self.language, k=self.k))),
                     ((f"y = {self.answer}."))]
        elif self.task_type == "max_x":
            steps = [((texts.t('s4', self.language))),
                     ((texts.t('s5', self.language, answer=self.answer)))]
        else:
            steps = [((texts.t('s6', self.language))),
                     ((texts.t('s7', self.language, answer=self.answer)))]
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
