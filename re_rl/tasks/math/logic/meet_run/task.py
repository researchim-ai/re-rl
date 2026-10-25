"""MeetRunTask — совместный прогон двух детерминированных автоматов.

Оба читают одно слово со своего старта. Символ считается, когда после него оба оказались в принимающих состояниях.
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


def meet_trace(trans_a: Table, accept_a: Sequence[int], trans_b: Table,
               accept_b: Sequence[int], word: Sequence[int]) -> List[Tuple[int, int, int, int]]:
    first = 0
    second = 0
    both = 0
    accept_first = set(accept_a)
    accept_second = set(accept_b)
    trace = []
    for symbol in word:
        first = trans_a[first][symbol]
        second = trans_b[second][symbol]
        flag = 1 if first in accept_first and second in accept_second else 0
        both += flag
        trace.append((first, second, both, flag))
    return trace


class MeetRunTask(BaseMathTask):
    TASK_TYPE = "meet_run"
    TASK_TYPES = ["both", "end"]

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
        self.trans_a, self.accept_a = self._machine()
        self.trans_b, self.accept_b = self._machine()
        self.word = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = meet_trace(self.trans_a, self.accept_a, self.trans_b, self.accept_b, self.word)
        self.both = self.trace[-1][2]
        self.at_end = self.trace[-1][3]
        self.answer = self.both if self.task_type == "both" else self.at_end
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _machine(self):
        trans = [[random.randrange(self.n), random.randrange(self.n)] for _ in range(self.n)]
        accept = tuple(sorted(random.sample(range(self.n), random.randint(1, self.n))))
        return trans, accept

    def _descr(self, language):
        shown = ", ".join(str(symbol) for symbol in self.word)
        accept_a = ", ".join(str(state) for state in self.accept_a)
        accept_b = ", ".join(str(state) for state in self.accept_b)
        key = "s0" if self.task_type == "both" else "s1"
        return texts.t(
            key, language, n=self.n, word=shown,
            accept_a=accept_a, trans_a=arrow_text(self.trans_a),
            accept_b=accept_b, trans_b=arrow_text(self.trans_b),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, first=first, second=second, both=both)
            for index, (symbol, (first, second, both, _flag)) in enumerate(zip(self.word, self.trace), 1)
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
