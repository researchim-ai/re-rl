"""RunLengthTask — серии одинаковых символов.

Символ 0 или 1. Новая серия начинается, когда символ меняется.
Длина строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def run_trace(symbols: Sequence[int]) -> Tuple[List[Tuple[int, int, int]], List[int]]:
    runs = 0
    last = None
    length = 0
    trace = []
    run_id = []
    for symbol in symbols:
        if symbol != last:
            runs += 1
            length = 1
            last = symbol
        else:
            length += 1
        trace.append((length, runs, symbol))
        run_id.append(runs)
    full = [0] * (runs + 1)
    for index, run in enumerate(run_id):
        full[run] = trace[index][0]
    return trace, full


class RunLengthTask(BaseMathTask):
    TASK_TYPE = "run_length"
    TASK_TYPES = ["runs", "span"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.symbols = [random.randint(0, 1) for _ in range(self.n)]
        self.trace, self.full = run_trace(self.symbols)
        self.runs = self.trace[-1][1]
        self.r = random.randint(1, self.runs)
        self.span = self.full[self.r]
        self.answer = self.runs if self.task_type == "runs" else self.span
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        symbols = ", ".join(str(symbol) for symbol in self.symbols)
        key = "s0" if self.task_type == "runs" else "s1"
        return texts.t(key, language, n=self.n, symbols=symbols, r=self.r)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, length=length, runs=runs)
            for index, ((length, runs, symbol)) in enumerate(self.trace, 1)
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
