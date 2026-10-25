"""WrapIndexTask — индекс в кольцевом массиве.

Индекс начинает с 0. Шаг +1 или -1 берётся по модулю длины массива.
Длина и число шагов равны и растут с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def wrap_trace(length: int, steps: Sequence[int]) -> List[Tuple[int, int]]:
    index = 0
    visits = 0
    trace = []
    for step in steps:
        index = (index + step) % length
        if index == 0:
            visits += 1
        trace.append((index, visits))
    return trace


class WrapIndexTask(BaseMathTask):
    TASK_TYPE = "wrap_index"
    TASK_TYPES = ["index", "visits"]

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
        self.steps = [random.choice((-1, 1)) for _ in range(self.n)]
        self.trace = wrap_trace(self.n, self.steps)
        self.index = self.trace[-1][0]
        self.visits = self.trace[-1][1]
        self.answer = self.index if self.task_type == "index" else self.visits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(step) for step in self.steps)
        key = "s0" if self.task_type == "index" else "s1"
        return texts.t(key, language, n=self.n, steps=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, step=step, place=place, visits=visits)
            for index, (step, (place, visits)) in enumerate(zip(self.steps, self.trace), 1)
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
