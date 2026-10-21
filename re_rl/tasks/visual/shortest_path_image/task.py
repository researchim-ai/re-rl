"""Визуальные варианты графовых задач: граф рисуется через networkx, а логика и
`verify` наследуются от текстовых задач.

- ``shortest_path_image`` — вес кратчайшего пути (исток/сток выделены цветом);
- ``mst_image``           — суммарный вес минимального остовного дерева;
- ``graph_coloring_image``— хроматическое число / k-раскрашиваемость;
- ``topological_sort_image`` — топологический порядок / наличие цикла (орграф);
- ``max_flow_image``      — величина максимального потока (сеть с пропускными).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import networkx as nx
from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.graph_algorithms_task import (
    WeightedShortestPathTask, MSTWeightTask, GraphColoringTask,
    TopologicalSortTask, MaxFlowTask,
)
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, fig_to_image
from re_rl.tasks.visual.graph_shared.base import _draw_graph

class ShortestPathVisualTask(VisualTaskMixin, WeightedShortestPathTask):
    TASK_TYPE = texts.literal('literals.s1')

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        hl = {self.src: "#8ce68c", self.dst: "#ff8c8c"}
        return _draw_graph(self.n, self.edges, weighted=True, highlight=hl,
                           seed=self.n + self.src, title=texts.t('s2', self.language))

    def _descr_visual(self, language):
        return ((texts.t('s0', language, src=self.src, dst=self.dst)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
