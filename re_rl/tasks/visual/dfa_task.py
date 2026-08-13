"""Визуальный вариант ДКА: диаграмма состояний и переходов (matplotlib).

Наследует логику от :class:`DFASimulationTask`: нужно определить, принимает ли
автомат заданную строку. Ответ да/нет, `verify` наследуется без изменений.
"""

import math
from collections import defaultdict

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.automata_sim_task import DFASimulationTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class DFAVisualTask(VisualTaskMixin, DFASimulationTask):
    TASK_TYPE = "dfa_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyArrowPatch, Circle
        m = self.m
        R = 2.4
        pos = {s: (R * math.cos(2 * math.pi * s / m + math.pi / 2),
                   R * math.sin(2 * math.pi * s / m + math.pi / 2)) for s in range(m)}
        fig, ax = plt.subplots(figsize=(5.2, 5.0))
        ax.set_aspect("equal"); ax.axis("off")
        rad = 0.45
        # рёбра: объединяем символы с одинаковым (s -> target)
        merged = defaultdict(list)
        for s in range(m):
            for sym in self.alphabet:
                merged[(s, self.delta[s][sym])].append(sym)
        for (s, t), syms in merged.items():
            label = ",".join(syms)
            x1, y1 = pos[s]; x2, y2 = pos[t]
            if s == t:  # петля
                lx, ly = x1 * 1.0, y1 * 1.0
                loop = Circle((x1 * 1.28, y1 * 1.28), 0.32, fill=False,
                              edgecolor="#555555", lw=1.4)
                ax.add_patch(loop)
                ax.text(x1 * 1.62, y1 * 1.62, label, ha="center", va="center", fontsize=11)
            else:
                # смещаем стрелку от края к краю окружностей + кривизна
                dx, dy = x2 - x1, y2 - y1
                d = math.hypot(dx, dy) or 1.0
                ux, uy = dx / d, dy / d
                start = (x1 + ux * rad, y1 + uy * rad)
                end = (x2 - ux * rad, y2 - uy * rad)
                arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15,
                                        color="#555555", lw=1.4,
                                        connectionstyle="arc3,rad=0.2")
                ax.add_patch(arrow)
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mx - uy * 0.35, my + ux * 0.35, label, ha="center", va="center",
                        fontsize=11, color="#b58900")
        for s in range(m):
            x, y = pos[s]
            ax.add_patch(Circle((x, y), rad, facecolor="#cfe8ff", edgecolor="#333333", lw=1.6))
            if s in self.accepting:  # двойной круг — принимающее
                ax.add_patch(Circle((x, y), rad * 0.78, fill=False, edgecolor="#333333", lw=1.2))
            ax.text(x, y, str(s), ha="center", va="center", fontsize=13, fontweight="bold")
        # стрелка «старт» в состояние 0
        sx, sy = pos[0]
        ax.add_patch(FancyArrowPatch((sx - 1.2, sy + 1.2), (sx - rad * 0.7, sy + rad * 0.7),
                                     arrowstyle="-|>", mutation_scale=15, color="#268bd2", lw=2))
        ax.text(sx - 1.3, sy + 1.35, "start", ha="right", va="bottom", fontsize=10,
                color="#268bd2")
        lim = R + 1.2
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.set_title(f"ДКА · строка: {self.word}")
        return fig_to_image(fig)

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На рисунке — диаграмма ДКА над алфавитом из символов a и b: начальное состояние "
                 f"отмечено стрелкой «start», принимающие — двойным кругом, дуги подписаны "
                 f"символами. Принимает ли автомат строку «{self.word}»? Ответьте да/нет.") if ru else
                (f"The figure shows a DFA diagram over the alphabet with symbols a and b: the start "
                 f"state has a 'start' arrow, accepting states are double circles, arcs are labeled "
                 f"by symbols. Does the automaton accept the string '{self.word}'? Answer yes/no."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
