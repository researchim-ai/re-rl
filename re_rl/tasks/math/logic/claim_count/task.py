"""ClaimCountTask — кто назвал верное число рыцарей.

Рыцарь говорит правду, лжец ошибается. Верным может быть только такое число,
которое назвали ровно столько человек. Число говорящих растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import Counter
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def consistent_counts(claims: Sequence[int]) -> List[int]:
    tally = Counter(claims)
    return sorted(claim for claim, votes in tally.items() if votes == claim)


class ClaimCountTask(BaseMathTask):
    TASK_TYPE = "claim_count"
    TASK_TYPES = ["count", "knight"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.count = random.randint(1, self.n - 1)
        knight_ids = set(random.sample(range(1, self.n + 1), self.count))
        self.claims = [self.count if index in knight_ids else self.n + 1 for index in range(1, self.n + 1)]
        self.consistent = consistent_counts(self.claims)
        self.k = random.randint(1, self.n)
        self.is_knight = 1 if self.claims[self.k - 1] == self.count else 0
        self.answer = self.count if self.task_type == "count" else self.is_knight
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{index}: {claim}" for index, claim in enumerate(self.claims, 1))
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        tally: Dict[int, int] = {}
        steps = []
        for index, claim in enumerate(self.claims, 1):
            tally[claim] = tally.get(claim, 0) + 1
            steps.append(texts.t("s2", self.language, i=index, claim=claim, votes=tally[claim]))
        steps.append(texts.t("s3", self.language, count=self.count, k=self.k, knight=self.is_knight))
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
