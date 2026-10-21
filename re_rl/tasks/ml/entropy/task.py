"""ShannonEntropyTask — энтропия Шеннона в битах.

Кратности исходов — степени двойки, их сумма тоже степень двойки, поэтому
H = log2(n) - (sum c log2 c) / n — точная дробь, без приближения логарифма.

Подтипы:
- ``value``   — энтропия одного распределения;
- ``compare`` — какое из двух распределений имеет большую энтропию (A или B).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def is_pow2(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def shannon_bits(counts: List[int]) -> Fraction:
    total = sum(counts)
    if not is_pow2(total):
        raise ValueError(texts.literal('literals.s4'))
    acc = 0
    for c in counts:
        if c == 0:
            continue
        if not is_pow2(c):
            raise ValueError(texts.literal('literals.s5'))
        acc += c * (c.bit_length() - 1)
    return Fraction(total * (total.bit_length() - 1) - acc, total)


def random_counts(total_exp: int, max_parts: int) -> List[int]:
    total = 1 << total_exp
    parts = [total]
    target = random.randint(2, max_parts)
    guard = 0
    while len(parts) < target and guard < 30:
        guard += 1
        i = random.randrange(len(parts))
        if parts[i] >= 2:
            parts[i] //= 2
            parts.append(parts[i])
    random.shuffle(parts)
    return parts


class ShannonEntropyTask(BaseMathTask):
    TASK_TYPE = "shannon_entropy"
    TASK_TYPES = ["value", "compare"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"exp": 2, "parts": 2}, 2: {"exp": 3, "parts": 2}, 3: {"exp": 3, "parts": 3},
        4: {"exp": 3, "parts": 3}, 5: {"exp": 4, "parts": 3}, 6: {"exp": 4, "parts": 4},
        7: {"exp": 4, "parts": 4}, 8: {"exp": 5, "parts": 4}, 9: {"exp": 5, "parts": 4},
        10: {"exp": 5, "parts": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.exp = int(p["exp"])
        self.parts = int(p["parts"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.counts_a = random_counts(self.exp, self.parts)
        self.h_a = shannon_bits(self.counts_a)
        if self.task_type == "compare":
            self.counts_b = random_counts(self.exp, self.parts)
            self.h_b = shannon_bits(self.counts_b)
            for _ in range(20):
                if self.h_a != self.h_b:
                    break
                self.counts_b = random_counts(self.exp, self.parts)
                self.h_b = shannon_bits(self.counts_b)
            if self.h_a == self.h_b:
                half = 1 << (self.exp - 1)
                self.counts_a = [half, half]
                self.h_a = shannon_bits(self.counts_a)
                self.counts_b = [1 << self.exp]
                self.h_b = shannon_bits(self.counts_b)
            self.answer_label = "A" if self.h_a > self.h_b else "B"
        else:
            self.answer_frac = self.h_a

    def _fmt_counts(self, counts: List[int]) -> str:
        return ", ".join(map(str, counts))

    def _descr(self, language):
        if self.task_type == "value":
            counts = self._fmt_counts(self.counts_a)
            return ((texts.t('s1', language, counts=counts)))
        a = self._fmt_counts(self.counts_a)
        b = self._fmt_counts(self.counts_b)
        return ((texts.t('s0', language, a=a, b=b)))

    def solve(self):
        if self.task_type == "value":
            shown = fmt_fraction(self.h_a)
            step = ((texts.t('s2', self.language, shown=shown)))
            self.final_answer = shown
        else:
            step = ((texts.t('s3', self.language, v0=fmt_fraction(self.h_a), v1=fmt_fraction(self.h_b))))
            self.final_answer = self.answer_label
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.final_answer)))]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "compare":
            return U.verify_label(prediction, [self.answer_label])
        return verify_fraction(prediction, self.h_a)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
