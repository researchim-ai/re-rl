"""Графовые алгоритмы как задачи с пошаговым решением.

Каждый класс — отдельный тип задачи с детерминированным алгоритмом-эталоном:
- WeightedShortestPathTask (Дейкстра),
- TopologicalSortTask (топосортировка / поиск цикла),
- GraphColoringTask (хроматическое число / k-раскрашиваемость),
- MSTWeightTask (вес остовного дерева, Крускал),
- EulerianPathTask (существование эйлерова пути),
- HamiltonianPathTask (существование гамильтонова пути),
- BipartiteMatchingTask (максимальное паросочетание, Кун),
- TSPTask (кратчайший гамильтонов цикл, перебор),
- MaxFlowTask (максимальный поток, Эдмондс–Карп),
- DAGLongestPathTask (длиннейший путь в DAG, ДП).
"""

import heapq
import random
from collections import defaultdict, deque
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _GraphBase(BaseMathTask):
    """Общие мелочи для графовых задач."""

    def _finish(self, description, language, detail_level, output_format, reasoning_mode):
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def get_result(self):
        result = super().get_result()
        if hasattr(self, 'algorithm_trace'):
            result['algorithm_trace'] = self.algorithm_trace
            directed = hasattr(self, 'cap_edges') or self.TASK_TYPE in (
                'topological_sort', 'topological_sort_image', 'dag_longest_path', 'floyd_distance', 'dag_paths', 'deadlock')
            directed = directed or getattr(self, 'directed', False)
            edges = getattr(self, 'cap_edges', getattr(self, 'wedges', getattr(self, 'edges', [])))
            result['graph'] = {'directed': directed, 'edges': [list(edge) for edge in edges]}
            if hasattr(self, 'L'):
                result['graph'].update(left_size=self.L, right_size=self.R,
                                       edges=[list(edge) for edge in self.pairs])
            else:
                if hasattr(self, 'n'):
                    result['graph']['n'] = self.n
            result['graph']['index_base'] = 1 if self.TASK_TYPE in ('tree_queries', 'tree_radius', 'tree_times', 'triangle_girth', 'wiener_index', 'dag_paths', 'shortest_path_count', 'prufer_code') else 0
            if hasattr(self, 'actions'):
                result['graph']['actions'] = [[[str(p), u] for p, u in action] for action in self.actions]
            if hasattr(self, 'd'):
                result['graph']['matrix'] = [row.copy() for row in self.d]
            for attribute in ('src', 'dst', 's', 't', 'k', 'subtype', 'task_type', 'parents', 'seq', 'branches', 'vertex', 'a', 'b', 'source', 'target'):
                if hasattr(self, attribute):
                    result['graph'][attribute] = getattr(self, attribute)
        return result

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task






























