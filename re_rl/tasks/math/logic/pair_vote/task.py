"""PairVoteTask — победитель всех попарных сравнений.

Кандидат побеждает другого только при строгом большинстве бюллетеней.
Число бюллетеней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Ballot = Tuple[int, int, int]


def condor_trace(ballots: Sequence[Ballot]) -> List[Tuple[int, int]]:
    ahead = [[0] * 4 for _ in range(4)]
    trace = []
    for ballot in ballots:
        rank = {candidate: place for place, candidate in enumerate(ballot)}
        for left in (1, 2, 3):
            for right in (1, 2, 3):
                if left != right and rank[left] < rank[right]:
                    ahead[left][right] += 1
        beats = []
        for left in (1, 2, 3):
            wins = 0
            for right in (1, 2, 3):
                if left != right and ahead[left][right] > ahead[right][left]:
                    wins += 1
            beats.append(wins)
        winner = 0
        for candidate, wins in enumerate(beats, 1):
            if wins == 2:
                winner = candidate
        trace.append((winner, beats[0]))
    return trace


class PairVoteTask(BaseMathTask):
    TASK_TYPE = "pair_vote"
    TASK_TYPES = ["winner", "wins"]

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
        self.ballots = []
        for _ in range(self.n):
            order = [1, 2, 3]
            random.shuffle(order)
            self.ballots.append(tuple(order))
        self.trace = condor_trace(self.ballots)
        self.winner = self.trace[-1][0]
        self.wins = self.trace[-1][1]
        self.answer = self.winner if self.task_type == "winner" else self.wins
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(" ".join(str(candidate) for candidate in ballot) for ballot in self.ballots)

    def _descr(self, language):
        key = "s0" if self.task_type == "winner" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, winner=winner, wins=wins)
            for index, (winner, wins) in enumerate(self.trace, 1)
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
