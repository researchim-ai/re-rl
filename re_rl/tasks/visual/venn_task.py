"""Диаграммы Венна (визуальная задача, matplotlib).

Два множества A и B с целыми элементами изображаются двумя пересекающимися
кругами; элементы расставлены по областям (только A, оба, только B) и вне кругов.
Данные считываются с рисунка.

Подтипы:
- ``intersection`` — |A ∩ B|;
- ``union``        — |A ∪ B|;
- ``only_a``       — число элементов только в A;
- ``sym_diff``     — |A △ B| (симметрическая разность).
"""

import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U


class VennDiagramTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "venn_diagram"
    TASK_TYPES = ["intersection", "union", "only_a", "sym_diff"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 2}, 2: {"m": 2}, 3: {"m": 3}, 4: {"m": 3}, 5: {"m": 4},
        6: {"m": 4}, 7: {"m": 5}, 8: {"m": 5}, 9: {"m": 6}, 10: {"m": 6},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        m = int(p["m"])
        self._build(m)
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self, m):
        pool = random.sample(range(1, 40), m * 4)
        idx = 0
        n_both = random.randint(1, m)
        n_a = random.randint(1, m)
        n_b = random.randint(1, m)
        n_out = random.randint(0, m)
        self.both = pool[idx:idx + n_both]; idx += n_both
        self.only_a = pool[idx:idx + n_a]; idx += n_a
        self.only_b = pool[idx:idx + n_b]; idx += n_b
        self.outside = pool[idx:idx + n_out]; idx += n_out
        if self.task_type == "intersection":
            self.answer = len(self.both)
        elif self.task_type == "union":
            self.answer = len(self.only_a) + len(self.only_b) + len(self.both)
        elif self.task_type == "only_a":
            self.answer = len(self.only_a)
        else:  # sym_diff
            self.answer = len(self.only_a) + len(self.only_b)

    def render_image(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle
        fig, ax = plt.subplots(figsize=(5.4, 4.2))
        ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Circle((-0.7, 0), 1.4, fill=True, facecolor="#268bd2", alpha=0.18,
                            edgecolor="#268bd2", lw=2))
        ax.add_patch(Circle((0.7, 0), 1.4, fill=True, facecolor="#dc322f", alpha=0.18,
                            edgecolor="#dc322f", lw=2))
        ax.text(-1.5, 1.35, "A", fontsize=16, color="#268bd2", fontweight="bold")
        ax.text(1.4, 1.35, "B", fontsize=16, color="#dc322f", fontweight="bold")

        def place(vals, cx):
            n = len(vals)
            if n == 0:
                return
            step = 0.42
            y0 = (n - 1) * step / 2.0
            for i, v in enumerate(vals):
                ax.text(cx, y0 - i * step, str(v), fontsize=12, ha="center", va="center")

        place(self.only_a, -1.35)
        place(self.only_b, 1.35)
        place(self.both, 0.0)
        # вне кругов
        for i, v in enumerate(self.outside):
            ax.text(-2.1 + i * 0.5, -1.7, str(v), fontsize=12, ha="center", va="center",
                    color="#666666")
        ax.set_xlim(-2.6, 2.6); ax.set_ylim(-2.1, 1.8)
        ax.set_title("Диаграмма Венна (U — все числа)")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        q = {
            "intersection": ("сколько элементов в пересечении A ∩ B (в общей области)?" if ru else
                             "how many elements are in the intersection A ∩ B (the overlap)?"),
            "union": ("сколько элементов в объединении A ∪ B?" if ru else
                      "how many elements are in the union A ∪ B?"),
            "only_a": ("сколько элементов только в A (в A, но не в B)?" if ru else
                       "how many elements are only in A (in A but not in B)?"),
            "sym_diff": ("сколько элементов в симметрической разности A △ B (ровно в одном из "
                         "множеств)?" if ru else
                         "how many elements are in the symmetric difference A △ B (in exactly one "
                         "set)?"),
        }[self.task_type]
        head = ("На диаграмме Венна показаны два множества A и B; числа расставлены по областям "
                "(числа вне кругов — вне обоих множеств). " if ru else
                "The Venn diagram shows two sets A and B; numbers are placed in the regions "
                "(numbers outside the circles are in neither set). ")
        return head + q

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Считаем элементы в нужных областях диаграммы." if ru else
             "Count the elements in the relevant regions of the diagram."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
