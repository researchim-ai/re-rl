"""BracketFinalTask — сетка на выбывание.

Соседи в текущем ряду играют, больший счёт проходит. Последний без пары проходит без игры.
Число матчей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def bracket_trace(scores: Sequence[int]) -> Tuple[List[Tuple[int, int, int]], int, int]:
    seats = list(range(len(scores)))
    trace = []
    while len(seats) > 1:
        nxt = []
        index = 0
        while index < len(seats):
            if index + 1 == len(seats):
                nxt.append(seats[index])
                break
            left = seats[index]
            right = seats[index + 1]
            winner = left if scores[left] >= scores[right] else right
            trace.append((left + 1, right + 1, winner + 1))
            nxt.append(winner)
            index += 2
        seats = nxt
    champion = seats[0] + 1
    last = trace[-1]
    finalist = last[1] if last[2] == last[0] else last[0]
    return trace, champion, finalist


class BracketFinalTask(BaseMathTask):
    TASK_TYPE = "bracket_final"
    TASK_TYPES = ["champion", "finalist"]

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
        self.scores = random.sample(range(1, self.n + 12), self.n + 1)
        self.trace, self.champion, self.finalist = bracket_trace(self.scores)
        assert len(self.trace) == self.n
        self.answer = self.champion if self.task_type == "champion" else self.finalist
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        scores = ", ".join(str(score) for score in self.scores)
        key = "s0" if self.task_type == "champion" else "s1"
        return texts.t(key, language, n=self.n, players=self.n + 1, scores=scores)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, winner=winner)
            for index, (left, right, winner) in enumerate(self.trace, 1)
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
