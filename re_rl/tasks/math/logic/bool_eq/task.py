"""BoolEqTask — равенства и неравенства булевых атомов.

Ограничение a=b или a!=b. Противоречие — когда уже выведенная связь нарушается.
z3 проверяет выполнимость всей системы.
Число ограничений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from z3 import Bool, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def eq_trace(size: int, constraints: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
    parent = list(range(size + 1))
    parity = [0] * (size + 1)

    def find(node: int) -> Tuple[int, int]:
        if parent[node] != node:
            root, flipped = find(parent[node])
            parity[node] ^= flipped
            parent[node] = root
        return parent[node], parity[node]

    ok = 1
    broke = 0
    trace = []
    for index, (left, right, diff) in enumerate(constraints, 1):
        if ok:
            root_l, par_l = find(left)
            root_r, par_r = find(right)
            if root_l == root_r:
                if (par_l ^ par_r) != diff:
                    ok = 0
                    broke = index
            else:
                parent[root_l] = root_r
                parity[root_l] = par_l ^ par_r ^ diff
        trace.append((ok, broke))
    return trace


def _z3_consistent(size: int, constraints: Sequence[Tuple[int, int, int]], ok: int) -> None:
    atoms = [None] + [Bool(str(index)) for index in range(1, size + 1)]
    solver = Solver()
    for left, right, diff in constraints:
        if diff:
            solver.add(atoms[left] != atoms[right])
        else:
            solver.add(atoms[left] == atoms[right])
    assert (solver.check() == sat) == bool(ok)


class BoolEqTask(BaseMathTask):
    TASK_TYPE = "bool_eq"
    TASK_TYPES = ["ok", "broke"]

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
        hidden = [0] + [random.randint(0, 1) for _ in range(self.n)]
        self.constraints: List[Tuple[int, int, int]] = []
        for index in range(self.n):
            left = random.randint(1, self.n)
            right = random.randint(1, self.n)
            diff = hidden[left] ^ hidden[right]
            if index == self.n - 1 and random.random() < 0.45:
                diff ^= 1
            self.constraints.append((left, right, diff))
        self.trace = eq_trace(self.n, self.constraints)
        self.ok = self.trace[-1][0]
        self.broke = self.trace[-1][1]
        _z3_consistent(self.n, self.constraints, self.ok)
        self.answer = self.ok if self.task_type == "ok" else self.broke
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{left}{'!=' if diff else '='}{right}" for left, right, diff in self.constraints)
        key = "s0" if self.task_type == "ok" else "s1"
        return texts.t(key, language, n=self.n, constraints=shown)

    def solve(self):
        steps = []
        for index, ((left, right, diff), (ok, broke)) in enumerate(zip(self.constraints, self.trace), 1):
            mark = "!=" if diff else "="
            steps.append(texts.t(
                "s2", self.language, i=index, left=left, mark=mark, right=right, ok=ok, broke=broke,
            ))
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
