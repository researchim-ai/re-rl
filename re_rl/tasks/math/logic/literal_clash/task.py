"""LiteralClashTask — столкновение литерала и его отрицания.

Список утверждает литералы по одному. Противоречие — атом и его отрицание оба встретились.
z3 проверяет совместность всего списка как единичных клауз.
Длина списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from z3 import Bool, Not, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def clash_trace(literals: Sequence[int]) -> List[Tuple[int, int]]:
    seen = {}
    first = 0
    var = 0
    trace = []
    for index, literal in enumerate(literals, 1):
        name = abs(literal)
        sign = 1 if literal > 0 else 0
        if name in seen and seen[name] != sign and first == 0:
            first = index
            var = name
        elif name not in seen:
            seen[name] = sign
        trace.append((first, var))
    return trace


def _z3_units(literals: Sequence[int], first: int) -> None:
    atoms = {}
    solver = Solver()
    for literal in literals:
        atom = atoms.setdefault(abs(literal), Bool(str(abs(literal))))
        solver.add(atom if literal > 0 else Not(atom))
    consistent = solver.check() == sat
    assert consistent == (first == 0)


class LiteralClashTask(BaseMathTask):
    TASK_TYPE = "literal_clash"
    TASK_TYPES = ["at", "var"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 9}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.literals = [random.choice((-1, 1)) * random.randint(1, self.n) for _ in range(self.n)]
        if random.random() < 0.7 and self.n >= 2:
            pos = random.randint(0, self.n - 2)
            later = random.randint(pos + 1, self.n - 1)
            self.literals[later] = -self.literals[pos]
        self.trace = clash_trace(self.literals)
        self.at, self.var = self.trace[-1]
        _z3_units(self.literals, self.at)
        self.answer = self.at if self.task_type == "at" else self.var
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        literals = ", ".join(str(literal) for literal in self.literals)
        key = "s0" if self.task_type == "at" else "s1"
        return texts.t(key, language, n=self.n, literals=literals)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, lit=lit, at=at, var=var)
            for index, (lit, (at, var)) in enumerate(zip(self.literals, self.trace), 1)
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
