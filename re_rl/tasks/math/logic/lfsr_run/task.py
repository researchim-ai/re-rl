"""LfsrRunTask — линейный регистр сдвига.

Левый бит выходит, новый бит равен сумме по модулю 2 битов на заданных позициях и встаёт справа.
Число шагов равно длине регистра и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lfsr_trace(bits: Sequence[int], taps: Sequence[int]) -> List[Tuple[int, int, int]]:
    state = list(bits)
    ones = 0
    trace = []
    for _step in range(len(bits)):
        out = state[0]
        new_bit = 0
        for tap in taps:
            new_bit ^= state[tap]
        state = state[1:] + [new_bit]
        ones += out
        reg = 0
        for bit in state:
            reg = (reg << 1) | bit
        trace.append((out, ones, reg))
    return trace


class LfsrRunTask(BaseMathTask):
    TASK_TYPE = "lfsr_run"
    TASK_TYPES = ["ones", "reg"]

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
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        if sum(self.bits) == 0:
            self.bits[0] = 1
        extra = random.randrange(1, self.n)
        self.taps = [0, extra]
        if self.n > 3 and random.randrange(2) == 1:
            self.taps.append(random.randrange(1, self.n))
        self.taps = sorted(set(self.taps))
        self.trace = lfsr_trace(self.bits, self.taps)
        self.ones = self.trace[-1][1]
        self.reg = self.trace[-1][2]
        self.answer = self.ones if self.task_type == "ones" else self.reg
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        taps = ", ".join(str(tap) for tap in self.taps)
        key = "s0" if self.task_type == "ones" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, taps=taps)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, out=out, ones=ones, reg=reg)
            for index, (out, ones, reg) in enumerate(self.trace, 1)
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
