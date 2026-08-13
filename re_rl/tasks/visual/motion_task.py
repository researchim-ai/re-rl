"""Графики движения (визуальные задачи, matplotlib).

- ``KinematicsGraphTask`` — график скорости v(t) (ломаная по целым узлам):
  подтипы ``displacement`` (перемещение = площадь под v–t) и ``acceleration``
  (ускорение на выделенном участке = наклон);
- ``ProjectileGraphTask`` — траектория брошенного тела (парабола):
  подтипы ``range`` (дальность) и ``max_height`` (максимальная высота).

Значения подобраны целыми и читаются по координатной сетке.
"""

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
        ax.set_xlabel("t, с"); ax.set_ylabel("v, м/с")
        ax.set_title("График скорости v(t)")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "displacement":
            return ("На графике показана скорость тела v(t) (шаг по времени 1 с). Найдите "
                    "перемещение за всё время — площадь под графиком (в метрах)." if ru else
                    "The graph shows a body's velocity v(t) (time step 1 s). Find the total "
                    "displacement — the area under the graph (in meters).")
        return ("На графике показана скорость v(t) (шаг по времени 1 с). Найдите ускорение на "
                "выделенном красным участке (в м/с²; может быть отрицательным)." if ru else
                "The graph shows velocity v(t) (time step 1 s). Find the acceleration on the "
                "red-highlighted segment (in m/s²; may be negative).")

    def solve(self):
        ru = self.language == "ru"
        a = self.answer
        a_str = f"{a:g}"
        if self.task_type == "displacement":
            step = ("Перемещение равно площади под v(t): сумма трапеций шириной 1 с." if ru else
                    "Displacement equals the area under v(t): sum of width-1 trapezoids.")
        else:
            step = ("Ускорение — наклон участка: (v₂−v₁)/Δt при Δt = 1 с." if ru else
                    "Acceleration is the segment slope: (v₂−v₁)/Δt with Δt = 1 s.")
        self.solution_steps = [step, (f"Ответ: {a_str}." if ru else f"Answer: {a_str}.")]
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
        ax.set_xlabel("x, м"); ax.set_ylabel("y, м")
        ax.set_aspect("auto")
        ax.set_title("Траектория брошенного тела")
        return fig_to_image(fig)

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "range":
            return ("На рисунке — траектория брошенного тела (парабола). Определите дальность "
                    "полёта — координату x, где тело возвращается на землю (y = 0)." if ru else
                    "The figure shows a projectile trajectory (a parabola). Find the range — the "
                    "x coordinate where the body returns to the ground (y = 0).")
        return ("На рисунке — траектория брошенного тела (парабола). Определите максимальную "
                "высоту подъёма." if ru else
                "The figure shows a projectile trajectory (a parabola). Find the maximum height.")

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "range":
            step = ("Дальность — точка, где парабола пересекает ось x справа." if ru else
                    "The range is where the parabola crosses the x-axis on the right.")
        else:
            step = ("Максимальная высота — ордината вершины параболы." if ru else
                    "The maximum height is the y coordinate of the parabola's vertex.")
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
