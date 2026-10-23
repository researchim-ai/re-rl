"""SternPathTask — путь по дереву Штерна–Броко.

Старт 1/1. Влево: a/b становится a/(a+b). Вправо: (a+b)/b.
Число шагов растёт с уровнем, дробь остаётся несократимой.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stern_walk(moves: Sequence[int]) -> List[Tuple[int, int]]:
    numer, denom = 1, 1
    trace = []
    for move in moves:
        if move == 0:
            denom = numer + denom
        else:
            numer = numer + denom
        trace.append((numer, denom))
    return trace


class SternPathTask(BaseMathTask):
    TASK_TYPE = "stern_path"
    TASK_TYPES = ["numer", "denom"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.moves = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = stern_walk(self.moves)
        self.numer, self.denom = self.trace[-1]
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _move_name(self, language, move: int) -> str:
        return texts.t("s4" if move == 0 else "s5", language)

    def _descr(self, language):
        listing = ", ".join(self._move_name(language, move) for move in self.moves)
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, (move, (numer, denom)) in enumerate(zip(self.moves, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, move=self._move_name(self.language, move),
                numer=numer, denom=denom,
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
