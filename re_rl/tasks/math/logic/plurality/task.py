"""PluralityTask — простое голосование.

Голос прибавляет одно очко кандидату. При равенстве побеждает меньший номер.
Число бюллетеней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def plurality_trace(votes: Sequence[int], candidates: int) -> Tuple[List[int], List[int]]:
    scores = [0] * (candidates + 1)
    winners = []
    for vote in votes:
        scores[vote] += 1
        winner = 1
        for candidate in range(2, candidates + 1):
            if scores[candidate] > scores[winner]:
                winner = candidate
        winners.append(winner)
    return scores, winners


class PluralityTask(BaseMathTask):
    TASK_TYPE = "plurality"
    TASK_TYPES = ["score", "winner"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "c": 3}, 2: {"n": 4, "c": 3}, 3: {"n": 5, "c": 3},
        4: {"n": 6, "c": 3}, 5: {"n": 7, "c": 4}, 6: {"n": 8, "c": 4},
        7: {"n": 10, "c": 4}, 8: {"n": 12, "c": 5}, 9: {"n": 14, "c": 5},
        10: {"n": 16, "c": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.candidates = max(2, int(p["c"]))
        self.votes = [random.randint(1, self.candidates) for _ in range(self.n)]
        self.scores, self.winners = plurality_trace(self.votes, self.candidates)
        self.k = random.randint(1, self.candidates)
        self.score = self.scores[self.k]
        self.winner = self.winners[-1]
        self.answer = self.score if self.task_type == "score" else self.winner
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(vote) for vote in self.votes)
        key = "s0" if self.task_type == "score" else "s1"
        return texts.t(
            key, language, n=self.n, candidates=self.candidates, listing=listing, k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, vote=vote, winner=winner)
            for index, (vote, winner) in enumerate(zip(self.votes, self.winners), 1)
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
