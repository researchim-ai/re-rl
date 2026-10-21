"""Чтение площади по графику (визуальная задача, matplotlib).

График — ломаная через целочисленные узлы на сетке; площадь считается точно по
формуле трапеций (шаг по x равен 1), поэтому задача полностью верифицируема.

Подтипы:
- ``under_curve``    — площадь между ломаной (y ≥ 0) и осью x;
- ``between_curves`` — площадь между двумя ломаными (верхняя ≥ нижней).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class AreaReadTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "area_read"
    TASK_TYPES = ["under_curve", "between_curves"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 3, "ymax": 5}, 2: {"k": 4, "ymax": 6}, 3: {"k": 4, "ymax": 7},
        4: {"k": 5, "ymax": 8}, 5: {"k": 5, "ymax": 9}, 6: {"k": 6, "ymax": 10},
        7: {"k": 7, "ymax": 10}, 8: {"k": 8, "ymax": 12}, 9: {"k": 9, "ymax": 12},
        10: {"k": 10, "ymax": 14},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.k = int(p["k"])
        self.ymax = int(p["ymax"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    @staticmethod
    def _trapz(ys: List[int]) -> float:
        return sum((ys[i] + ys[i + 1]) / 2.0 for i in range(len(ys) - 1))

    def _build(self):
        self.xs = list(range(self.k + 1))
        if self.task_type == "under_curve":
            self.ys = [random.randint(0, self.ymax) for _ in range(self.k + 1)]
            self.answer = self._trapz(self.ys)
        else:
            self.bottom = [random.randint(0, self.ymax // 2) for _ in range(self.k + 1)]
            self.top = [self.bottom[i] + random.randint(1, max(1, self.ymax - self.bottom[i]))
                        for i in range(self.k + 1)]
            self.answer = self._trapz(self.top) - self._trapz(self.bottom)

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
        if self.task_type == "under_curve":
            ax.plot(self.xs, self.ys, "-o", color="#268bd2", linewidth=2)
            ax.fill_between(self.xs, self.ys, color="#268bd2", alpha=0.2)
        else:
            ax.plot(self.xs, self.top, "-o", color="#dc322f", linewidth=2, label=texts.t('s5', self.language))
            ax.plot(self.xs, self.bottom, "-o", color="#268bd2", linewidth=2, label=texts.t('s6', self.language))
            ax.fill_between(self.xs, self.bottom, self.top, color="#859900", alpha=0.25)
            ax.legend(loc="upper right", fontsize=8)
        ax.set_xticks(self.xs)
        ax.set_yticks(range(0, self.ymax + 2))
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.set_title(texts.t('s4', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "under_curve":
            return ((texts.t('s1', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        a = self.answer
        a_str = f"{a:g}"
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            ((texts.t('s3', self.language, a_str=a_str)))]
        self.final_answer = a_str

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_value(prediction, float(self.answer), tol=1e-3)

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
