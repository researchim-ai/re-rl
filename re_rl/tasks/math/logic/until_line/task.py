"""UntilLineTask — временной оператор «пока не».

Из позиции i идём вправо. Если встретился q, формула истинна. Если встретился мир без p и без q, формула ложна.
Число миров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def until_trace(hold: Sequence[int], stop: Sequence[int]) -> List[Tuple[int, int]]:
    size = len(hold)
    trace = []
    total = 0
    for start in range(size):
        holds = 0
        for index in range(start, size):
            if stop[index]:
                holds = 1
                break
            if not hold[index]:
                break
        total += holds
        trace.append((holds, total))
    return trace


class UntilLineTask(BaseMathTask):
    TASK_TYPE = "until_line"
    TASK_TYPES = ["count", "here"]

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
        self.hold = [random.randint(0, 1) for _ in range(self.n)]
        self.stop = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = until_trace(self.hold, self.stop)
        self.count = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.trace[self.k - 1][0]
        self.answer = self.count if self.task_type == "count" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        hold = ", ".join(str(bit) for bit in self.hold)
        stop = ", ".join(str(bit) for bit in self.stop)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, hold=hold, stop=stop, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, holds=holds, total=total)
            for index, (holds, total) in enumerate(self.trace, 1)
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
