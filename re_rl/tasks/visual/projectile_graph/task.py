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

class ProjectileGraphTask(VisualTaskMixin, BaseMathTask):
    TASK_TYPE = "projectile_graph"
    TASK_TYPES = ["range", "max_height"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rmax": 6, "hmax": 4}, 2: {"rmax": 8, "hmax": 5}, 3: {"rmax": 10, "hmax": 6},
        4: {"rmax": 12, "hmax": 7}, 5: {"rmax": 14, "hmax": 8}, 6: {"rmax": 16, "hmax": 9},
        7: {"rmax": 18, "hmax": 10}, 8: {"rmax": 20, "hmax": 11}, 9: {"rmax": 24, "hmax": 12},
        10: {"rmax": 28, "hmax": 14},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.rmax = int(p["rmax"])
        self.hmax = int(p["hmax"])
        self._build()
        super().__init__(self._descr(language), language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build(self):
        self.R = random.randrange(4, self.rmax + 1, 2)  # чётная — пик в целой точке R/2
        self.H = random.randint(2, self.hmax)
        self.answer = self.R if self.task_type == "range" else self.H

    def render_image(self):
        import matplotlib.pyplot as plt
        import numpy as np
        xs = np.linspace(0, self.R, 200)
        ys = 4 * self.H * xs * (self.R - xs) / (self.R ** 2)
        fig, ax = plt.subplots(figsize=(5.4, 3.8))
        ax.plot(xs, ys, color="#dc322f", linewidth=2)
        ax.plot([0, self.R], [0, 0], "ko", markersize=5)
        ax.set_xticks(range(0, self.R + 1, max(1, self.R // 10)))
        ax.set_yticks(range(0, self.H + 2))
        ax.grid(True, linestyle=":", alpha=0.7)
        ax.set_xlabel(texts.t('s4', self.language)); ax.set_ylabel(texts.t('s5', self.language))
        ax.set_aspect("auto")
        ax.set_title(texts.t('s6', self.language))
        return fig_to_image(fig)

    def _descr(self, language):
        if self.task_type == "range":
            return ((texts.t('s1', language)))
        return ((texts.t('s0', language)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "range":
            step = ((texts.t('s2', self.language)))
        else:
            step = ((texts.t('s3', self.language)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
