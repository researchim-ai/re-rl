"""QuorumRiseTask — голосования с растущим порогом.

Если голосов «за» хватает на текущий порог, решение принято и порог увеличивается на 1.
Число голосований растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def play_votes(votes: Sequence[int], quorum: int) -> Tuple[int, int, List[Tuple[int, int, int]]]:
    passed = 0
    trace = []
    for ballot in votes:
        before = quorum
        accepted = 1 if ballot >= quorum else 0
        if accepted:
            passed += 1
            quorum += 1
        trace.append((before, accepted, quorum))
    return passed, quorum, trace


class QuorumRiseTask(BaseMathTask):
    TASK_TYPE = "quorum_rise"
    TASK_TYPES = ["passed", "before"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "q": 2, "v": 3}, 2: {"n": 2, "q": 2, "v": 4},
        3: {"n": 3, "q": 3, "v": 4}, 4: {"n": 3, "q": 3, "v": 5},
        5: {"n": 4, "q": 3, "v": 5}, 6: {"n": 5, "q": 4, "v": 6},
        7: {"n": 6, "q": 4, "v": 6}, 8: {"n": 7, "q": 4, "v": 7},
        9: {"n": 8, "q": 5, "v": 7}, 10: {"n": 10, "q": 5, "v": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(1, max(1, int(p["q"])))
        self.votes = [random.randint(0, max(1, int(p["v"]))) for _ in range(self.n)]
        self.passed, self.final_quorum, self.trace = play_votes(self.votes, self.start)
        self.k = random.randint(1, self.n)
        self.before = self.trace[self.k - 1][0]
        self.answer = self.passed if self.task_type == "passed" else self.before
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(ballot) for ballot in self.votes)
        key = "s0" if self.task_type == "passed" else "s1"
        return texts.t(key, language, n=self.n, q0=self.start, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, before=before, votes=ballot, ok=ok, after=after)
            for index, ((before, ok, after), ballot) in enumerate(zip(self.trace, self.votes), 1)
        ]
        steps.append(texts.t("s3", self.language, passed=self.passed, quorum=self.final_quorum))
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
