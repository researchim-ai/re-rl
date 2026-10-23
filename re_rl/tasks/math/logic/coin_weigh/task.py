"""CoinWeighTask — поиск одного тяжёлого предмета по взвешиваниям.

На левой чаше перевес кодируется -1, на правой 1, равновесие 0.
Число взвешиваний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Weighing = Tuple[Tuple[int, ...], Tuple[int, ...], int]


def weigh_trace(items: int, weighings: Sequence[Weighing]) -> List[Tuple[int, int, int]]:
    possible = set(range(1, items + 1))
    seen = 0
    trace = []
    for index, (left, right, outcome) in enumerate(weighings, 1):
        left_set = set(left)
        right_set = set(right)
        nxt: Set[int] = set()
        for item in possible:
            if item in left_set:
                predicted = -1
            elif item in right_set:
                predicted = 1
            else:
                predicted = 0
            if predicted == outcome:
                nxt.add(item)
        possible = nxt
        if seen == 0 and len(possible) == 1:
            seen = index
        only = min(possible) if len(possible) == 1 else 0
        trace.append((len(possible), seen, only))
    return trace


class CoinWeighTask(BaseMathTask):
    TASK_TYPE = "coin_weigh"
    TASK_TYPES = ["heavy", "seen"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6},
        9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.items = self.n + 2
        self.heavy = random.randint(1, self.items)
        self.weighings = [self._weighing() for _ in range(self.n)]
        self.trace = weigh_trace(self.items, self.weighings)
        _, self.seen, self.only = self.trace[-1]
        self.answer = self.only if self.task_type == "heavy" else self.seen
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _weighing(self) -> Weighing:
        pool = list(range(1, self.items + 1))
        random.shuffle(pool)
        take = random.randint(2, min(4, self.items))
        group = pool[:take]
        mid = max(1, len(group) // 2)
        left = tuple(sorted(group[:mid]))
        right = tuple(sorted(group[mid:]))
        if self.heavy in left:
            outcome = -1
        elif self.heavy in right:
            outcome = 1
        else:
            outcome = 0
        return left, right, outcome

    def _side(self, group: Sequence[int]) -> str:
        return " ".join(str(item) for item in group)

    def _descr(self, language):
        rows = []
        for left, right, outcome in self.weighings:
            word = texts.t("s4" if outcome < 0 else "s5" if outcome > 0 else "s6", language)
            rows.append(f"{self._side(left)} / {self._side(right)} / {word}")
        listing = "; ".join(rows)
        key = "s0" if self.task_type == "heavy" else "s1"
        return texts.t(key, language, items=self.items, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, possible=possible, seen=seen, only=only)
            for index, (possible, seen, only) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t("s3", self.language, heavy=self.only, seen=self.seen))
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
