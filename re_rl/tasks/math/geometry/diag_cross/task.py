"""DiagCrossTask — пересечения диагоналей выпуклого многоугольника.

Каждые четыре вершины дают ровно одну точку пересечения диагоналей внутри.
Число вершин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def diag_quads(vertices: int) -> List[Tuple[int, int, int, int]]:
    quads = []
    for a in range(1, vertices + 1):
        for b in range(a + 1, vertices + 1):
            for c in range(b + 1, vertices + 1):
                for d in range(c + 1, vertices + 1):
                    quads.append((a, b, c, d))
    return quads


class DiagCrossTask(BaseMathTask):
    TASK_TYPE = "diag_cross"
    TASK_TYPES = ["count", "top"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.vertices = max(5, int(p["n"]))
        self.n = self.vertices
        self.quads = diag_quads(self.vertices)
        self.count = len(self.quads)
        self.k = random.randint(1, self.count)
        self.top = self.quads[self.k - 1][3]
        self.answer = self.count if self.task_type == "count" else self.top
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.vertices, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, a=a, b=b, c=c, d=d)
            for index, (a, b, c, d) in enumerate(self.quads, 1)
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
