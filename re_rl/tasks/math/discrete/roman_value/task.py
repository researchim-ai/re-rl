"""RomanValueTask — значение строки из римских знаков.

Если знак меньше следующего, он вычитается. Иначе прибавляется.
Длина строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

VALUES = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
SYMBOLS = ("I", "V", "X", "L", "C")


def roman_trace(symbols: Sequence[str]) -> List[Tuple[int, int]]:
    vals = [VALUES[symbol] for symbol in symbols]
    total = 0
    subs = 0
    trace = []
    for index, value in enumerate(vals):
        if index + 1 < len(vals) and value < vals[index + 1]:
            total -= value
            subs += 1
        else:
            total += value
        trace.append((total, subs))
    return trace


class RomanValueTask(BaseMathTask):
    TASK_TYPE = "roman_value"
    TASK_TYPES = ["value", "subs"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.symbols = [random.choice(SYMBOLS) for _ in range(self.n)]
        self.trace = roman_trace(self.symbols)
        self.value, self.subs = self.trace[-1]
        self.answer = self.value if self.task_type == "value" else self.subs
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(self.symbols)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, total=total, subs=subs)
            for index, (symbol, (total, subs)) in enumerate(zip(self.symbols, self.trace), 1)
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
