"""ClampAddTask — прибавление с удержанием в отрезке.

После прибавления число ниже 0 становится 0, а число выше верхней границы становится этой границей.
Верхняя граница равна числу шагов. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def clamp_trace(start: int, limit: int, deltas: Sequence[int]) -> List[Tuple[int, int]]:
    value = start
    clips = 0
    trace = []
    for delta in deltas:
        value += delta
        if value < 0:
            value = 0
            clips += 1
        elif value > limit:
            value = limit
            clips += 1
        trace.append((value, clips))
    return trace


class ClampAddTask(BaseMathTask):
    TASK_TYPE = "clamp_add"
    TASK_TYPES = ["value", "clips"]

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
        self.start = random.randint(0, self.n)
        self.deltas = [random.randint(-3, 4) for _ in range(self.n)]
        self.trace = clamp_trace(self.start, self.n, self.deltas)
        self.value = self.trace[-1][0]
        self.clips = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.clips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(delta) for delta in self.deltas)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, deltas=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, delta=delta, value=value, clips=clips)
            for index, (delta, (value, clips)) in enumerate(zip(self.deltas, self.trace), 1)
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
