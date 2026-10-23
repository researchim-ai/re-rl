"""LockLogTask — захват и отпуск замков.

Повторный захват и отпуск свободного замка считаются ошибкой и состояние не меняют.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[str, int]


def lock_trace(locks: int, ops: Sequence[Op]) -> List[Tuple[int, List[int]]]:
    held = [0] * (locks + 1)
    fails = 0
    trace = []
    for kind, index in ops:
        if kind == "get":
            if held[index]:
                fails += 1
            else:
                held[index] = 1
        elif held[index]:
            held[index] = 0
        else:
            fails += 1
        trace.append((fails, list(held)))
    return trace


class LockLogTask(BaseMathTask):
    TASK_TYPE = "lock_log"
    TASK_TYPES = ["fails", "held"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.locks = 2
        self.ops = []
        held = [0, 0, 0]
        for _ in range(self.n):
            index = random.randint(1, self.locks)
            if held[index] and random.random() < 0.6:
                kind = "put"
                held[index] = 0
            else:
                kind = "get"
                if not held[index]:
                    held[index] = 1
            self.ops.append((kind, index))
        self.trace = lock_trace(self.locks, self.ops)
        self.k = random.randint(1, self.locks)
        self.fails = self.trace[-1][0]
        self.held = self.trace[-1][1][self.k]
        self.answer = self.fails if self.task_type == "fails" else self.held
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _phrase(self, op, language):
        kind, index = op
        return texts.t("s4" if kind == "get" else "s5", language, lock=index)

    def _descr(self, language):
        listing = "; ".join(self._phrase(op, language) for op in self.ops)
        key = "s0" if self.task_type == "fails" else "s1"
        return texts.t(key, language, n=self.n, locks=self.locks, listing=listing, k=self.k)

    def solve(self):
        steps = []
        for index, (op, (fails, held)) in enumerate(zip(self.ops, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, phrase=self._phrase(op, self.language),
                fails=fails, held=held[self.k],
            ))
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
