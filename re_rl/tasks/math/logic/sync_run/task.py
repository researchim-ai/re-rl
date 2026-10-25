"""SyncRunTask — сколько состояний склеивает одно слово.

Одно и то же слово читается сразу из всех состояний детерминированного автомата. После символа остаётся образ множества.
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


def image_trace(trans: Table, word: Sequence[int]) -> List[Tuple[int, int]]:
    current = set(range(len(trans)))
    trace = []
    for symbol in word:
        current = {trans[state][symbol] for state in current}
        trace.append((len(current), int(len(current) == 1)))
    return trace


class SyncRunTask(BaseMathTask):
    TASK_TYPE = "sync_run"
    TASK_TYPES = ["left", "synced"]

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
        self.trans = [[random.randrange(self.n), random.randrange(self.n)] for _ in range(self.n)]
        self.word = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = image_trace(self.trans, self.word)
        self.left = self.trace[-1][0]
        self.synced = self.trace[-1][1]
        self.answer = self.left if self.task_type == "left" else self.synced
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(symbol) for symbol in self.word)
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(key, language, n=self.n, trans=arrow_text(self.trans), word=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, symbol=symbol, left=left, synced=synced)
            for index, (symbol, (left, synced)) in enumerate(zip(self.word, self.trace), 1)
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
