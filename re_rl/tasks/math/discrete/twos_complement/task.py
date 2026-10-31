"""TwosComplementTask — дополнительный код (two's complement).

Подтипы:
- ``decode``   — по n-битному коду в дополнительном коде найти знаковое число;
- ``encode``   — представить знаковое число в n-битном дополнительном коде (биты);
- ``overflow`` — возникает ли знаковое переполнение при сложении двух n-битных чисел.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import re
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class TwosComplementTask(BaseMathTask):
    TASK_TYPE = "twos_complement"
    TASK_TYPES = ["decode", "encode", "overflow"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"bits": 4}, 2: {"bits": 4}, 3: {"bits": 5}, 4: {"bits": 6}, 5: {"bits": 6},
        6: {"bits": 8}, 7: {"bits": 8}, 8: {"bits": 10}, 9: {"bits": 12}, 10: {"bits": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.bits = int(p["bits"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _lo_hi(self):
        n = self.bits
        return -(1 << (n - 1)), (1 << (n - 1)) - 1

    def _to_bits(self, value: int) -> str:
        return format(value & ((1 << self.bits) - 1), f"0{self.bits}b")

    def _from_bits(self, bits: str) -> int:
        u = int(bits, 2)
        if bits[0] == "1":
            u -= (1 << self.bits)
        return u

    def _build(self):
        lo, hi = self._lo_hi()
        if self.task_type == "decode":
            self.value = random.randint(lo, hi)
            self.bits_str = self._to_bits(self.value)
            self.answer = self.value
        elif self.task_type == "encode":
            self.value = random.randint(lo, hi)
            self.answer = self._to_bits(self.value)
        else:  # overflow
            self.a = random.randint(lo, hi)
            self.b = random.randint(lo, hi)
            s = self.a + self.b
            self.overflow = not (lo <= s <= hi)
            self.answer = self.overflow

    def _descr(self, language):
        n = self.bits
        if self.task_type == "decode":
            return ((texts.t('s1', language, n=n, bits_str=self.bits_str)))
        if self.task_type == "encode":
            return ((texts.t('s2', language, value=self.value, n=n, n_2=n)))
        return ((texts.t('s0', language, n=n, v1=self._lo_hi()[0], v2=self._lo_hi()[1], a=self.a, b=self.b)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "decode":
            steps = [((texts.t('s3', self.language))),
                     ((texts.common('answer_line', self.language, answer=self.value)))]
            self.final_answer = str(self.value)
        elif self.task_type == "encode":
            steps = [((texts.t('s6', self.language))),
                     ((texts.common('answer_line', self.language, answer=self.answer)))]
            self.final_answer = self.answer
        else:
            ans = (texts.t('s4', self.language) if self.overflow else texts.t('s5', self.language))
            steps = [((texts.t('s7', self.language))),
                     ((texts.common('answer_line', self.language, answer=ans)))]
            self.final_answer = ans
        self.solution_steps = steps

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "decode":
            return U.verify_int(prediction, int(self.value))
        if self.task_type == "overflow":
            return U.verify_bool(prediction, bool(self.overflow))
        # encode: сравниваем битовую строку
        txt = U.clean(prediction)
        m = re.findall(r"[01]{2,}", txt.replace(" ", "").replace("_", ""))
        if not m:
            return 0.0
        cand = max(m, key=len)
        return 1.0 if cand == self.answer else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
