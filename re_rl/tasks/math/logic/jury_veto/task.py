"""JuryVetoTask — большинство и право вето.

Решение принято, если голосов «за» не меньше порога и вето не против.
Число присяжных растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def jury_trace(votes: Sequence[int], threshold: int, veto: int) -> Tuple[List[Tuple[int, int]], int]:
    yes = 0
    blocked = 0
    trace = []
    for index, vote in enumerate(votes, 1):
        yes += vote
        if index == veto and vote == 0:
            blocked = 1
        trace.append((yes, blocked))
    convict = 1 if yes >= threshold and blocked == 0 else 0
    return trace, convict


class JuryVetoTask(BaseMathTask):
    TASK_TYPE = "jury_veto"
    TASK_TYPES = ["yes", "convict"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "t": 2}, 2: {"n": 3, "t": 2}, 3: {"n": 4, "t": 2},
        4: {"n": 5, "t": 3}, 5: {"n": 6, "t": 3}, 6: {"n": 7, "t": 4},
        7: {"n": 8, "t": 4}, 8: {"n": 9, "t": 5}, 9: {"n": 10, "t": 5},
        10: {"n": 12, "t": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.threshold = int(p["t"])
        self.votes = [random.randint(0, 1) for _ in range(self.n)]
        self.veto = random.randint(1, self.n)
        self.trace, self.convict = jury_trace(self.votes, self.threshold, self.veto)
        self.yes = self.trace[-1][0]
        self.answer = self.yes if self.task_type == "yes" else self.convict
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        votes = ", ".join(str(vote) for vote in self.votes)
        key = "s0" if self.task_type == "yes" else "s1"
        return texts.t(
            key, language, n=self.n, votes=votes,
            threshold=self.threshold, veto=self.veto,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, vote=vote, yes=yes, blocked=blocked)
            for index, (vote, (yes, blocked)) in enumerate(zip(self.votes, self.trace), 1)
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
