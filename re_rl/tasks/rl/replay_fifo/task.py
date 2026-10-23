"""ReplayFifoTask — кольцевой буфер опыта.

Новое значение встаёт в конец. При переполнении выпадает самое старое.
Число записей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fifo_trace(values: Sequence[int], capacity: int) -> List[Tuple[List[int], int]]:
    buffer: List[int] = []
    overwrites = 0
    trace = []
    for value in values:
        if len(buffer) < capacity:
            buffer.append(value)
        else:
            buffer.pop(0)
            buffer.append(value)
            overwrites += 1
        trace.append((list(buffer), overwrites))
    return trace


class ReplayFifoTask(BaseMathTask):
    TASK_TYPE = "replay_fifo"
    TASK_TYPES = ["slot", "overwrites"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "c": 3}, 2: {"n": 4, "c": 3}, 3: {"n": 5, "c": 3},
        4: {"n": 6, "c": 4}, 5: {"n": 7, "c": 4}, 6: {"n": 8, "c": 4},
        7: {"n": 10, "c": 5}, 8: {"n": 11, "c": 5}, 9: {"n": 12, "c": 5},
        10: {"n": 14, "c": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.capacity = max(1, int(p["c"]))
        self.values = [random.randint(1, 9) for _ in range(self.n)]
        self.trace = fifo_trace(self.values, self.capacity)
        self.buffer, self.overwrites = self.trace[-1]
        self.k = random.randint(1, len(self.buffer))
        self.slot = self.buffer[self.k - 1]
        self.answer = self.slot if self.task_type == "slot" else self.overwrites
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "slot" else "s1"
        return texts.t(
            key, language, n=self.n, capacity=self.capacity, listing=listing, k=self.k,
        )

    def solve(self):
        steps = []
        for index, (value, (buffer, overwrites)) in enumerate(zip(self.values, self.trace), 1):
            shown = ", ".join(str(item) for item in buffer)
            steps.append(texts.t(
                "s2", self.language, i=index, value=value, buffer=shown, overwrites=overwrites,
            ))
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
