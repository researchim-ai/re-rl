"""Визуальный вариант PV-цикла: P–V диаграмма замкнутого цикла (matplotlib).

Наследует логику от :class:`PVCycleTask` (подтип net_work): работа газа за цикл
равна площади, охватываемой контуром. Вершины подписаны координатами (V, P),
поэтому данные считываются с рисунка. Проверка числовая (наследуется).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.physics.thermodynamics.pv_cycle_task import PVCycleTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image


class PVCycleVisualTask(VisualTaskMixin, PVCycleTask):
    TASK_TYPE = texts.literal('literals.s3')
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
        ax.set_xlabel(texts.t('s5', self.language))
        ax.set_ylabel(texts.t('s6', self.language))
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_title(texts.t('s7', self.language))
        return fig_to_image(fig)

    def solve(self):
        # Работа по модулю (площадь контура) — не зависит от направления обхода.
        from re_rl.tasks.physics._phys_utils import fmt
        W = abs(self._cycle_work())
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language))),
            texts.t('s8', self.language, v0=fmt(W)),
        ]
        self.final_answer = texts.t('s4', self.language, v0=fmt(W))
        self._answer_numbers = [W]

    def _descr_visual(self, language):
        n = len(self.points)
        return ((texts.t('s0', language, n=n)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode)
        task.solve()
        return task
