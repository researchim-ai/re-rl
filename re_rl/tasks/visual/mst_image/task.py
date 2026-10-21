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

class MSTVisualTask(VisualTaskMixin, MSTWeightTask):
    TASK_TYPE = "mst_image"

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def render_image(self):
        return _draw_graph(self.n, self.edges, weighted=True, seed=self.n * 3,
                           title=texts.t('s1', self.language))

    def _descr_visual(self, language):
        return ((texts.t('s0', language)))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
