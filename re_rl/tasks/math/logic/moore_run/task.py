"""MooreRunTask — сумма чисел, которые печатает автомат Мура.

В каждом состоянии напечатано одно число. Стрелки детерминированы, печать стартового состояния входит в сумму.
Длина слова растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Table = Sequence[Sequence[int]]


def arrow_text(trans: Table) -> str:
    parts = []
    for state, row in enumerate(trans):
        for symbol, target in enumerate(row):
            parts.append(f"{state},{symbol}: {target}")
    return "; ".join(parts)


def moore_trace(outputs: Sequence[int], trans: Table, word: Sequence[int]) -> List[Tuple[int, int, int]]:
    state = 0
    total = outputs[0]
    trace = []
    for symbol in word:
        state = trans[state][symbol]
        total += outputs[state]
        trace.append((state, outputs[state], total))
    return trace


class MooreRunTask(BaseMathTask):
    TASK_TYPE = "moore_run"
    TASK_TYPES = ["total", "last"]

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
        self.outputs = [random.randint(0, 4) for _ in range(self.n)]
        self.trans = [[random.randrange(self.n), random.randrange(self.n)] for _ in range(self.n)]
        self.word = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = moore_trace(self.outputs, self.trans, self.word)
        self.total = self.trace[-1][2]
        self.last = self.trace[-1][1]
        self.answer = self.total if self.task_type == "total" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(symbol) for symbol in self.word)
        outs = "; ".join(f"{state}: {out}" for state, out in enumerate(self.outputs))
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, outs=outs, trans=arrow_text(self.trans), word=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, state=state, out=out, total=total)
            for index, (symbol, (state, out, total)) in enumerate(zip(self.word, self.trace), 1)
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
