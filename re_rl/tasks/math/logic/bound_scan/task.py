"""BoundScanTask — единственное целое в пересечении границ.

Каждое ограничение вида x >= a или x <= b сужает отрезок.
Набор построен так, что остаётся ровно одно целое.
Число ограничений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Constraint = Tuple[str, int]


def make_constraints(count: int, target: int, lo: int, hi: int) -> List[Constraint]:
    constraints: List[Constraint] = []
    cur_lo, cur_hi = lo, hi
    for _ in range(max(0, count - 2)):
        if random.randrange(2) == 0:
            bound = random.randint(cur_lo, target)
            constraints.append(("ge", bound))
            cur_lo = max(cur_lo, bound)
        else:
            bound = random.randint(target, cur_hi)
            constraints.append(("le", bound))
            cur_hi = min(cur_hi, bound)
    if cur_lo < target:
        constraints.append(("ge", target))
        cur_lo = target
    if cur_hi > target:
        constraints.append(("le", target))
        cur_hi = target
    while len(constraints) < count:
        kind = "ge" if random.randrange(2) == 0 else "le"
        constraints.append((kind, target))
    random.shuffle(constraints)
    return constraints


def scan_bounds(lo: int, hi: int, constraints: Sequence[Constraint]):
    tight = 0
    history = []
    for kind, bound in constraints:
        if kind == "ge":
            nxt = max(lo, bound)
            changed = nxt != lo
            lo = nxt
        else:
            nxt = min(hi, bound)
            changed = nxt != hi
            hi = nxt
        if changed:
            tight += 1
        history.append((lo, hi))
    return lo, hi, tight, history


class BoundScanTask(BaseMathTask):
    TASK_TYPE = "bound_scan"
    TASK_TYPES = ["value", "tight"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.target = random.randint(0, 12)
        self.lo = self.target - 30
        self.hi = self.target + 30
        self.constraints = make_constraints(self.n, self.target, self.lo, self.hi)
        end_lo, end_hi, self.tight, self.history = scan_bounds(self.lo, self.hi, self.constraints)
        assert end_lo == end_hi == self.target
        self.value = end_lo
        self.answer = self.value if self.task_type == "value" else self.tight
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _piece(self, language, kind: str, bound: int) -> str:
        key = "s4" if kind == "ge" else "s5"
        return texts.t(key, language, value=bound)

    def _descr(self, language):
        listing = "; ".join(self._piece(language, kind, bound) for kind, bound in self.constraints)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, lo=self.lo, hi=self.hi, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, ((kind, bound), (lo, hi)) in enumerate(zip(self.constraints, self.history), 1):
            piece = self._piece(self.language, kind, bound)
            steps.append(texts.t("s2", self.language, i=index, piece=piece, lo=lo, hi=hi))
        steps.append(texts.t("s3", self.language, value=self.value, tight=self.tight))
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
