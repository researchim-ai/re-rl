"""PathTollTask — плата за проход по заданному маршруту.

Ребро есть только если оно перечислено. Первое отсутствующее ребро останавливает путь.
Число шагов маршрута растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Edge = Tuple[int, int]


def toll_trace(edges: Dict[Edge, int], walk: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    stop = 0
    trace = []
    for index in range(len(walk) - 1):
        key = (walk[index], walk[index + 1])
        if stop == 0 and key in edges:
            total += edges[key]
        elif stop == 0:
            stop = index + 1
        trace.append((total, stop))
    return trace


class PathTollTask(BaseMathTask):
    TASK_TYPE = "path_toll"
    TASK_TYPES = ["toll", "stop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.edges = {}
        for _ in range(self.n):
            src = random.randint(1, 4)
            dst = random.randint(1, 4)
            self.edges[(src, dst)] = random.randint(1, 6)
        self.walk = [random.randint(1, 4) for _ in range(self.n + 1)]
        self.trace = toll_trace(self.edges, self.walk)
        self.toll, self.stop = self.trace[-1]
        self.answer = self.toll if self.task_type == "toll" else self.stop
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        roads = "; ".join(f"{src} {dst} {cost}" for (src, dst), cost in sorted(self.edges.items()))
        walk = ", ".join(str(node) for node in self.walk)
        key = "s0" if self.task_type == "toll" else "s1"
        return texts.t(key, language, n=self.n, roads=roads, walk=walk)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, toll=toll, stop=stop)
            for index, (toll, stop) in enumerate(self.trace, 1)
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
