"""NfaRunTask — прогон недетерминированного автомата.

По одному символу из текущего множества выходят все стрелки. Символ считается принятым, если среди новых состояний есть принимающее.
Длина слова растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = List[Tuple[int, ...]]


def arrow_text(trans: Sequence[Row]) -> str:
    parts = []
    for state, row in enumerate(trans):
        for symbol, targets in enumerate(row):
            shown = " ".join(str(target) for target in targets)
            parts.append(f"{state},{symbol}: {shown}")
    return "; ".join(parts)


def nfa_trace(trans: Sequence[Row], accept: Sequence[int], word: Sequence[int]) -> List[Tuple[int, int, int]]:
    current = {0}
    accept_set = set(accept)
    visits = 0
    trace = []
    for symbol in word:
        reached = set()
        for state in current:
            reached.update(trans[state][symbol])
        current = reached
        hit = 1 if current & accept_set else 0
        visits += hit
        trace.append((len(current), hit, visits))
    return trace


class NfaRunTask(BaseMathTask):
    TASK_TYPE = "nfa_run"
    TASK_TYPES = ["visits", "hit"]

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
        self.trans = []
        for _state in range(self.n):
            row = []
            for _symbol in range(2):
                first = random.randrange(self.n)
                if random.randrange(2) == 1:
                    other = (first + 1) % self.n
                    row.append(tuple(sorted((first, other))))
                else:
                    row.append((first,))
            self.trans.append(row)
        if len(self.trans[0][0]) == 1:
            first = self.trans[0][0][0]
            other = (first + 1) % self.n
            self.trans[0][0] = tuple(sorted((first, other)))
        self.accept = tuple(sorted(random.sample(range(self.n), random.randint(1, self.n))))
        self.word = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = nfa_trace(self.trans, self.accept, self.word)
        self.hit = self.trace[-1][1]
        self.visits = self.trace[-1][2]
        self.answer = self.visits if self.task_type == "visits" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(symbol) for symbol in self.word)
        accept = ", ".join(str(state) for state in self.accept)
        arrows = arrow_text(self.trans)
        key = "s0" if self.task_type == "visits" else "s1"
        return texts.t(key, language, n=self.n, accept=accept, word=shown, trans=arrows)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, reach=reach, hit=hit, visits=visits)
            for index, (symbol, (reach, hit, visits)) in enumerate(zip(self.word, self.trace), 1)
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
