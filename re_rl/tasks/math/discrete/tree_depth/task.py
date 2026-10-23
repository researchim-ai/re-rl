"""TreeDepthTask — глубины в дереве с известными родителями.

Узел 1 — корень. Родитель каждого следующего узла имеет меньший номер.
Число узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def tree_depths(parents: Sequence[int]) -> List[int]:
    depth = [0] * len(parents)
    for node in range(2, len(parents)):
        depth[node] = depth[parents[node]] + 1
    return depth


class TreeDepthTask(BaseMathTask):
    TASK_TYPE = "tree_depth"
    TASK_TYPES = ["depth", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 11},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.parents = [0, 0]
        for node in range(2, self.n + 1):
            self.parents.append(random.randint(1, node - 1))
        self.depths = tree_depths(self.parents)
        self.k = random.randint(1, self.n)
        self.depth = self.depths[self.k]
        self.total = sum(self.depths[1:])
        self.answer = self.depth if self.task_type == "depth" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{node}-{self.parents[node]}" for node in range(2, self.n + 1))
        key = "s0" if self.task_type == "depth" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=node, parent=self.parents[node], depth=self.depths[node])
            for node in range(1, self.n + 1)
        ]
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
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
