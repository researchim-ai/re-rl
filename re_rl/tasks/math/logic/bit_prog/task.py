"""BitProgTask — программа над четырёхбитным регистром.

Код 0 — и, 1 — или, 2 — исключающее или, 3 — сдвиг влево на 1 с отсечением до четырёх битов.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def bit_ones(value: int) -> int:
    return bin(value).count("1")


def bit_trace(start: int, ops: Sequence[Op]) -> List[Tuple[int, int]]:
    reg = start
    trace = []
    for code, mask in ops:
        if code == 0:
            reg &= mask
        elif code == 1:
            reg |= mask
        elif code == 2:
            reg ^= mask
        else:
            reg = (reg << 1) & 15
        trace.append((reg, bit_ones(reg)))
    return trace


class BitProgTask(BaseMathTask):
    TASK_TYPE = "bit_prog"
    TASK_TYPES = ["reg", "ones"]

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
        self.start = random.randint(0, 15)
        self.ops = [(random.randint(0, 3), random.randint(0, 15)) for _ in range(self.n)]
        self.trace = bit_trace(self.start, self.ops)
        self.reg = self.trace[-1][0]
        self.ones = self.trace[-1][1]
        self.answer = self.reg if self.task_type == "reg" else self.ones
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{code} {mask}" for code, mask in self.ops)
        key = "s0" if self.task_type == "reg" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=code, mask=mask, reg=reg, ones=ones)
            for index, ((code, mask), (reg, ones)) in enumerate(zip(self.ops, self.trace), 1)
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
