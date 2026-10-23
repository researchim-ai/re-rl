"""SignalEdgesTask — фронты и самая длинная единица в сигнале.

Фронт — переход из 0 в 1. Длина сигнала растёт с уровнем. Один проход.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def signal_trace(bits: Sequence[int]) -> List[Tuple[int, int]]:
    rises = 0
    longest = 0
    run = 0
    previous = 0
    trace = []
    for bit in bits:
        if previous == 0 and bit == 1:
            rises += 1
        if bit == 1:
            run += 1
            if run > longest:
                longest = run
        else:
            run = 0
        previous = bit
        trace.append((rises, longest))
    return trace


class SignalEdgesTask(BaseMathTask):
    TASK_TYPE = "signal_edges"
    TASK_TYPES = ["rises", "longest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = signal_trace(self.bits)
        self.rises, self.longest = self.trace[-1]
        self.answer = self.rises if self.task_type == "rises" else self.longest
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "rises" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, rises=rises, longest=longest)
            for index, (bit, (rises, longest)) in enumerate(zip(self.bits, self.trace), 1)
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
