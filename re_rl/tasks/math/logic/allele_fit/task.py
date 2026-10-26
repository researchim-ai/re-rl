"""AlleleFitTask — возможны ли аллели ребёнка.

Каждый родитель отдаёт один аллель из своей пары, порядок внутри пары не важен.
Число проверок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]
Claim = Tuple[Pair, Pair, Pair]


def allele_trace(claims: Sequence[Claim]) -> List[Tuple[int, int]]:
    bad = 0
    first = 0
    trace = []
    for index, (left, right, child) in enumerate(claims, 1):
        left_set = set(left)
        right_set = set(right)
        one, two = child
        possible = (one in left_set and two in right_set) or (one in right_set and two in left_set)
        if not possible:
            bad += 1
            if first == 0:
                first = index
        trace.append((bad, first))
    return trace


class AlleleFitTask(BaseMathTask):
    TASK_TYPE = "allele_fit"
    TASK_TYPES = ["bad", "first"]

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
        self.claims = []
        for _ in range(self.n):
            self.claims.append((
                (random.randint(0, 2), random.randint(0, 2)),
                (random.randint(0, 2), random.randint(0, 2)),
                (random.randint(0, 2), random.randint(0, 2)),
            ))
        self.trace = allele_trace(self.claims)
        self.bad = self.trace[-1][0]
        self.first = self.trace[-1][1]
        self.answer = self.bad if self.task_type == "bad" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        parts = []
        for left, right, child in self.claims:
            parts.append(
                f"{left[0]} {left[1]} + {right[0]} {right[1]} -> {child[0]} {child[1]}"
            )
        return "; ".join(parts)

    def _descr(self, language):
        key = "s0" if self.task_type == "bad" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bad=bad, first=first)
            for index, (bad, first) in enumerate(self.trace, 1)
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
