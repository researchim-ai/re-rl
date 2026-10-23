"""MuxIndexTask — выбор значения битами адреса.

Биты читаются слева направо, старший первый. Адрес собирается удвоением и прибавлением бита.
Число битов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mux_trace(bits: Sequence[int]) -> List[int]:
    index = 0
    trace = []
    for bit in bits:
        index = index * 2 + bit
        trace.append(index)
    return trace


class MuxIndexTask(BaseMathTask):
    TASK_TYPE = "mux_index"
    TASK_TYPES = ["index", "value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5},
        9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.values = [random.randint(0, 9) for _ in range(2 ** self.n)]
        self.trace = mux_trace(self.bits)
        self.index = self.trace[-1]
        self.value = self.values[self.index]
        self.answer = self.index if self.task_type == "index" else self.value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        values = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "index" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, values=values)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, address=address)
            for index, (bit, address) in enumerate(zip(self.bits, self.trace), 1)
        ]
        steps.append(texts.t("s3", self.language, index=self.index, value=self.value))
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
