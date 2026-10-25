"""PtrWalkTask — переход по массиву следующих номеров.

Каждая клетка хранит номер следующей. Старт в нуле, шагов столько же, сколько клеток.
Число клеток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ptr_trace(nxt: Sequence[int]) -> List[Tuple[int, int]]:
    index = 0
    zeros = 0
    trace = []
    for _ in nxt:
        index = nxt[index]
        if index == 0:
            zeros += 1
        trace.append((index, zeros))
    return trace


class PtrWalkTask(BaseMathTask):
    TASK_TYPE = "ptr_walk"
    TASK_TYPES = ["land", "zeros"]

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
        self.nxt = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.trace = ptr_trace(self.nxt)
        self.land = self.trace[-1][0]
        self.zeros = self.trace[-1][1]
        self.answer = self.land if self.task_type == "land" else self.zeros
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(item) for item in self.nxt)
        key = "s0" if self.task_type == "land" else "s1"
        return texts.t(key, language, n=self.n, nxt=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, place=place, zeros=zeros)
            for index, (place, zeros) in enumerate(self.trace, 1)
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
