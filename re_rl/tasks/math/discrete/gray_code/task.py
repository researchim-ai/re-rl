"""GrayCodeTask — двоично-отражённый код Грея.

Код числа n равен n XOR (n >> 1). Декодирование восстанавливает n побитовым XOR.

Подтипы:
- ``encode`` — n в коде Грея, ровно width бит;
- ``decode`` — целое по строке кода Грея.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import re
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def gray_encode(n: int) -> int:
    return n ^ (n >> 1)


def gray_decode(g: int) -> int:
    n = 0
    while g:
        n ^= g
        g >>= 1
    return n


class GrayCodeTask(BaseMathTask):
    TASK_TYPE = "gray_code"
    TASK_TYPES = ["encode", "decode"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"width": 3}, 2: {"width": 4}, 3: {"width": 4}, 4: {"width": 5},
        5: {"width": 6}, 6: {"width": 7}, 7: {"width": 8}, 8: {"width": 9},
        9: {"width": 10}, 10: {"width": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.width = int(p["width"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.value = random.randrange(1 << self.width)
        self.bits = format(gray_encode(self.value), f"0{self.width}b")
        if gray_decode(int(self.bits, 2)) != self.value:
            raise RuntimeError(texts.t('s4', language))
        self.answer = self.bits if self.task_type == "encode" else self.value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "encode":
            return ((texts.t('s1', language, value=self.value, width=self.width)))
        return ((texts.t('s0', language, bits=self.bits, width=self.width)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "encode":
            step = ((texts.t('s2', self.language, value=self.value, v1=self.value >> 1, v2=int(self.bits, 2), width=self.width, bits=self.bits)))
            self.final_answer = self.bits
        else:
            step = ((texts.t('s3', self.language, value=self.value)))
            self.final_answer = str(self.value)
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.final_answer)))]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "decode":
            return U.verify_int(prediction, self.value)
        txt = U.clean(prediction).replace(" ", "").replace("_", "")
        runs = re.findall(rf"[01]{{{self.width}}}", txt)
        return 1.0 if self.bits in runs else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
