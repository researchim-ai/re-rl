"""CayleyTreesTask — число деревьев на помеченных вершинах.

Для v вершин при v не меньше 2 это v в степени v-2. Степень собирается умножениями.
Число умножений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cayley_trace(vertices: int) -> List[int]:
    value = 1
    trace = []
    for _ in range(max(0, vertices - 2)):
        value *= vertices
        trace.append(value)
    return trace


class CayleyTreesTask(BaseMathTask):
    TASK_TYPE = "cayley_trees"
    TASK_TYPES = ["trees", "part"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 4}, 2: {"v": 4}, 3: {"v": 5}, 4: {"v": 6},
        5: {"v": 7}, 6: {"v": 8}, 7: {"v": 9}, 8: {"v": 10},
        9: {"v": 12}, 10: {"v": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.vertices = max(2, int(p["v"]))
        self.n = self.vertices - 2
        self.trace = cayley_trace(self.vertices)
        self.trees = self.trace[-1]
        self.k = random.randint(1, self.n)
        self.part = self.trace[self.k - 1]
        self.answer = self.trees if self.task_type == "trees" else self.part
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "trees" else "s1"
        return texts.t(key, language, vertices=self.vertices, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value)
            for index, value in enumerate(self.trace, 1)
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
