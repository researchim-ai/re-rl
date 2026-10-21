"""Графики движения (визуальные задачи, matplotlib).

- ``KinematicsGraphTask`` — график скорости v(t) (ломаная по целым узлам):
  подтипы ``displacement`` (перемещение = площадь под v–t) и ``acceleration``
  (ускорение на выделенном участке = наклон);
- ``ProjectileGraphTask`` — траектория брошенного тела (парабола):
  подтипы ``range`` (дальность) и ``max_height`` (максимальная высота).

Значения подобраны целыми и читаются по координатной сетке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.math.logic import _logic_utils as U

class KinematicsGraphTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "kinematics_graph"
    TASK_TYPES = ["displacement", "acceleration"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 3, "vmax": 5}, 2: {"k": 4, "vmax": 6}, 3: {"k": 4, "vmax": 7},
        4: {"k": 5, "vmax": 8}, 5: {"k": 5, "vmax": 9}, 6: {"k": 6, "vmax": 10},
        7: {"k": 7, "vmax": 10}, 8: {"k": 8, "vmax": 12}, 9: {"k": 9, "vmax": 12},
        10: {"k": 10, "vmax": 14},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.k = int(p["k"])
        self.vmax = int(p["vmax"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        self.ts = list(range(self.k + 1))
        self.vs = [random.randint(0, self.vmax) for _ in range(self.k + 1)]
        if self.task_type == "displacement":
            self.answer = sum((self.vs[i] + self.vs[i + 1]) / 2.0 for i in range(self.k))
        else:  # acceleration на выделенном участке
            self.seg = random.randrange(self.k)
            # гарантируем ненулевой (наглядный) наклон
            for _ in range(20):
                if self.vs[self.seg + 1] != self.vs[self.seg]:
                    break
                self.vs[self.seg + 1] = random.randint(0, self.vmax)
            self.answer = self.vs[self.seg + 1] - self.vs[self.seg]  # Δv / Δt, Δt = 1

    def render_image(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(5.2, 3.8))
        ax.plot(self.ts, self.vs, "-o", color="#268bd2", linewidth=2)
        if self.task_type == "displacement":
            ax.fill_between(self.ts, self.vs, color="#268bd2", alpha=0.2)
        else:
            s = self.seg
            ax.plot([self.ts[s], self.ts[s + 1]], [self.vs[s], self.vs[s + 1]],
                    color="#dc322f", linewidth=4)
        ax.set_xticks(self.ts)
        ax.set_yticks(range(0, self.vmax + 2))
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.set_xlabel(texts.t('s4', self.language)); ax.set_ylabel(texts.t('s5', self.language))
        ax.set_title(texts.t('s6', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "displacement":
            return ((texts.t('s1', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        a = self.answer
        a_str = f"{a:g}"
        if self.task_type == "displacement":
            step = ((texts.t('s2', self.language)))
        else:
            step = ((texts.t('s3', self.language)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=a_str)))]
        self.final_answer = a_str

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "displacement":
            return U.verify_value(prediction, float(self.answer), tol=1e-3)
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
