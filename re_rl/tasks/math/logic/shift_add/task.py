"""ShiftAddTask — умножение сдвигами и сложениями.

Биты множителя идут от младшего к старшему. Единица прибавляет текущий сдвиг.
Число битов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def shift_add(value: int, bits: Sequence[int]) -> Tuple[int, int, List[int]]:
    acc = 0
    shifted = value
    adds = 0
    totals = []
    for bit in bits:
        if bit:
            acc += shifted
            adds += 1
        totals.append(acc)
        shifted *= 2
    return acc, adds, totals


class ShiftAddTask(BaseMathTask):
    TASK_TYPE = "shift_add"
    TASK_TYPES = ["product", "adds"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 4}, 2: {"n": 2, "m": 6}, 3: {"n": 3, "m": 6},
        4: {"n": 3, "m": 8}, 5: {"n": 4, "m": 8}, 6: {"n": 5, "m": 8},
        7: {"n": 6, "m": 9}, 8: {"n": 7, "m": 9}, 9: {"n": 8, "m": 9},
        10: {"n": 10, "m": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.value = random.randint(1, max(1, int(p["m"])))
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        if sum(self.bits) == 0:
            self.bits[0] = 1
        self.product, self.adds, self.totals = shift_add(self.value, self.bits)
        self.multiplier = sum(bit << index for index, bit in enumerate(self.bits))
        self.answer = self.product if self.task_type == "product" else self.adds
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "product" else "s1"
        return texts.t(key, language, value=self.value, n=self.n, listing=listing)

    def solve(self):
        shifted = self.value
        steps = []
        for index, (bit, total) in enumerate(zip(self.bits, self.totals), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, bit=bit, shifted=shifted, total=total,
            ))
            shifted *= 2
        steps.append(texts.t("s3", self.language, product=self.product, adds=self.adds))
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
