"""Визуальный вариант PV-цикла: P–V диаграмма замкнутого цикла (matplotlib).

Наследует логику от :class:`PVCycleTask` (подтип net_work): работа газа за цикл
равна площади, охватываемой контуром. Вершины подписаны координатами (V, P),
поэтому данные считываются с рисунка. Проверка числовая (наследуется).
"""

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.physics.thermodynamics.pv_cycle_task import PVCycleTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class PVCycleVisualTask(VisualTaskMixin, PVCycleTask):
    TASK_TYPE = "pv_cycle_image"
    TASK_TYPES = ["net_work"]

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False, **kwargs):
        super().__init__(task_type="net_work", language=language, detail_level=detail_level,
                         difficulty=difficulty, output_format=output_format,
                         reasoning_mode=reasoning_mode)
        self.description = self._descr_visual(language)

    def render_image(self):
        import matplotlib.pyplot as plt
        pts = self.points + [self.points[0]]
        vs = [v for v, _ in pts]
        ps = [p for _, p in pts]
        fig, ax = plt.subplots(figsize=(5.2, 4.6))
        ax.plot(vs, ps, "-o", color="#268bd2", linewidth=2, markersize=6)
        ax.fill(vs, ps, color="#268bd2", alpha=0.12)
        for i, (v, p) in enumerate(self.points):
            ax.annotate(f"({v}, {p})", (v, p), textcoords="offset points", xytext=(6, 6),
                        fontsize=9)
        ax.set_xlabel("V, м³")
        ax.set_ylabel("P, Па")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title("P–V диаграмма цикла")
        return fig_to_image(fig)

    def solve(self):
        # Работа по модулю (площадь контура) — не зависит от направления обхода.
        from re_rl.tasks.physics._phys_utils import fmt
        W = abs(self._cycle_work())
        ru = self.language == "ru"
        self.solution_steps = [
            ("Работа газа за цикл по модулю равна площади, охватываемой контуром на P–V диаграмме."
             if ru else
             "The gas work per cycle (absolute value) equals the area enclosed by the P–V loop."),
            ("Площадь считаем формулой шнурков по координатам вершин." if ru else
             "Compute the area via the shoelace formula over the vertices."),
            f"W = {fmt(W)} Дж",
        ]
        self.final_answer = f"W = {fmt(W)} Дж"
        self._answer_numbers = [W]

    def _descr_visual(self, language):
        ru = language == "ru"
        n = len(self.points)
        return ((f"На рисунке — P–V диаграмма замкнутого термодинамического цикла из {n} вершин "
                 f"(координаты каждой вершины (V, P) подписаны). Найдите работу газа за цикл (по "
                 f"модулю), равную площади, охватываемой контуром. Ответ в джоулях.") if ru else
                (f"The figure shows a P–V diagram of a closed thermodynamic cycle with {n} vertices "
                 f"(each vertex is labeled with its (V, P)). Find the work done by the gas per cycle "
                 f"(absolute value), equal to the area enclosed by the loop. Answer in joules."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task
