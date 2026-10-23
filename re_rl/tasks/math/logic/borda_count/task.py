"""BordaCountTask — баллы Борда по нескольким бюллетеням.

Первое место даёт на один балл меньше, чем число кандидатов, последнее даёт 0.
Число бюллетеней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def borda_scores(rankings: Sequence[Sequence[int]], candidates: int) -> List[List[int]]:
    scores = [0] * candidates
    history = []
    for ranking in rankings:
        for place, candidate in enumerate(ranking):
            scores[candidate - 1] += candidates - 1 - place
        history.append(list(scores))
    return history


def borda_winner(scores: Sequence[int]) -> int:
    best = max(scores)
    return min(index for index, score in enumerate(scores) if score == best) + 1


class BordaCountTask(BaseMathTask):
    TASK_TYPE = "borda_count"
    TASK_TYPES = ["score", "winner"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "c": 3}, 2: {"n": 3, "c": 3}, 3: {"n": 4, "c": 3},
        4: {"n": 4, "c": 3}, 5: {"n": 5, "c": 4}, 6: {"n": 6, "c": 4},
        7: {"n": 7, "c": 4}, 8: {"n": 8, "c": 4}, 9: {"n": 10, "c": 5},
        10: {"n": 12, "c": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.candidates = max(3, int(p["c"]))
        order = list(range(1, self.candidates + 1))
        self.rankings = []
        for _ in range(self.n):
            random.shuffle(order)
            self.rankings.append(list(order))
        self.history = borda_scores(self.rankings, self.candidates)
        self.scores = self.history[-1]
        self.k = random.randint(1, self.candidates)
        self.score = self.scores[self.k - 1]
        self.winner = borda_winner(self.scores)
        self.answer = self.score if self.task_type == "score" else self.winner
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            ">".join(str(candidate) for candidate in ranking)
            for ranking in self.rankings
        )
        key = "s0" if self.task_type == "score" else "s1"
        return texts.t(
            key, language, n=self.n, candidates=self.candidates, listing=listing, k=self.k,
        )

    def solve(self):
        steps = []
        for index, scores in enumerate(self.history, 1):
            shown = ", ".join(str(score) for score in scores)
            steps.append(texts.t("s2", self.language, i=index, scores=shown))
        steps.append(texts.t("s3", self.language, k=self.k, score=self.score, winner=self.winner))
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
