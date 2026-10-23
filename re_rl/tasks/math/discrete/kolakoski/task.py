"""KolakoskiTask — последовательность Колакоски.

Она состоит из 1 и 2. Длины её серий сами читаются как эта последовательность.
Начало 1, 2, 2. Длина растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def run_lengths(seq: List[int]) -> List[int]:
    lengths = []
    index = 0
    while index < len(seq):
        end = index
        while end < len(seq) and seq[end] == seq[index]:
            end += 1
        lengths.append(end - index)
        index = end
    return lengths


def kolakoski_full(length: int) -> List[int]:
    seq = [1, 2, 2]
    cursor = 2
    while len(seq) < length:
        symbol = 3 - seq[-1]
        seq.extend([symbol] * seq[cursor])
        cursor += 1
    assert run_lengths(seq) == seq[: len(run_lengths(seq))]
    return seq


class KolakoskiTask(BaseMathTask):
    TASK_TYPE = "kolakoski"
    TASK_TYPES = ["symbol", "ones"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 6}, 3: {"n": 8}, 4: {"n": 10},
        5: {"n": 12}, 6: {"n": 14}, 7: {"n": 16}, 8: {"n": 18},
        9: {"n": 20}, 10: {"n": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.full = kolakoski_full(self.n)
        self.trace = self.full[: self.n]
        self.k = random.randint(1, self.n)
        self.symbol = self.trace[self.k - 1]
        self.ones = self.trace.count(1)
        self.answer = self.symbol if self.task_type == "symbol" else self.ones
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "symbol" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol)
            for index, symbol in enumerate(self.trace, 1)
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
