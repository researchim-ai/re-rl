"""TreeMisTask — максимальное независимое множество дерева.

В множестве нет двух вершин, соединённых ребром. Дерево задаётся списком рёбер.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def tree_mis(n: int, edges: Sequence[Tuple[int, int]]) -> int:
    adj: List[List[int]] = [[] for _ in range(n)]
    for src, dst in edges:
        adj[src].append(dst)
        adj[dst].append(src)

    def dfs(node: int, parent: int) -> Tuple[int, int]:
        take = 1
        skip = 0
        for child in adj[node]:
            if child == parent:
                continue
            child_skip, child_take = dfs(child, node)
            take += child_skip
            skip += max(child_skip, child_take)
        return skip, take

    skip, take = dfs(0, -1)
    return max(skip, take)


class TreeMisTask(BaseMathTask):
    TASK_TYPE = "tree_mis"
    TASK_TYPES = ["size"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 7}, 5: {"n": 8},
        6: {"n": 9}, 7: {"n": 10}, 8: {"n": 12}, 9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = "size"
        self.augment = augment
        self.edges = [(i, random.randrange(i)) for i in range(1, self.n)]
        self.answer = tree_mis(self.n, self.edges)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _shown(self) -> str:
        return ", ".join(f"{src + 1}-{dst + 1}" for src, dst in self.edges)

    def _descr(self, language):
        return ((texts.t('s0', language, n=self.n, v1=self._shown())))

    def solve(self):
        step = ((texts.t('s1', self.language, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
