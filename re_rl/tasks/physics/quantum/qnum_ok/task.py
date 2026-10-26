"""QnumOkTask — допустимые четвёрки квантовых чисел.

n не меньше 1, l лежит от 0 до n-1, m лежит от -l до l, спин равен 1 или -1.
Число четвёрок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

State = Tuple[int, int, int, int]


def _allowed(principal: int, angular: int, magnetic: int, spin: int) -> bool:
    return (
        principal >= 1
        and 0 <= angular <= principal - 1
        and abs(magnetic) <= angular
        and spin in (-1, 1)
    )


def qnum_trace(states: Sequence[State]) -> List[Tuple[int, int]]:
    valid = 0
    first = 0
    trace = []
    for index, state in enumerate(states, 1):
        if _allowed(*state):
            valid += 1
        elif first == 0:
            first = index
        trace.append((valid, first))
    return trace


class QnumOkTask(BaseMathTask):
    TASK_TYPE = "qnum_ok"
    TASK_TYPES = ["valid", "first"]

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
        self.states = []
        for _ in range(self.n):
            principal = random.randint(1, 4)
            angular = random.randint(0, principal + 1)
            magnetic = random.randint(-(angular + 1), angular + 1)
            spin = random.choice((-1, 1, 0))
            self.states.append((principal, angular, magnetic, spin))
        self.trace = qnum_trace(self.states)
        self.valid = self.trace[-1][0]
        self.first = self.trace[-1][1]
        self.answer = self.valid if self.task_type == "valid" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(
            f"{principal} {angular} {magnetic} {spin}"
            for principal, angular, magnetic, spin in self.states
        )

    def _descr(self, language):
        key = "s0" if self.task_type == "valid" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, valid=valid, first=first)
            for index, (valid, first) in enumerate(self.trace, 1)
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
