"""ResolveProofTask — проверка цепочки резолюции.

Каждый шаг вычёркивает переменную, которая входит в две клаузы с противоположными знаками.
Пустая клауза имеет длину 0. z3 проверяет выполнимость исходного набора.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from z3 import Bool, Not, Or, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def resolve(left: Sequence[int], right: Sequence[int], var: int) -> List[int]:
    if var in left and -var in right:
        positive, negative = left, right
    elif -var in left and var in right:
        positive, negative = right, left
    else:
        raise ValueError(var)
    merged = [lit for lit in positive if lit != var] + [lit for lit in negative if lit != -var]
    result = []
    for lit in merged:
        if lit not in result:
            result.append(lit)
    return result


def resolution_trace(chain: int, cancel: bool) -> Tuple[List[List[int]], List[List[int]]]:
    clauses = [[1]]
    for var in range(1, chain):
        clauses.append([-var, var + 1])
    if cancel:
        clauses.append([-chain])
    else:
        clauses.append([-chain, chain + 1])
    current = [1]
    derived = []
    for var in range(1, chain + 1):
        current = resolve(current, clauses[var], var)
        derived.append(list(current))
    return clauses, derived


def _sat_matches(clauses: Sequence[Sequence[int]], empty: bool) -> None:
    atoms = {}

    def lit(value: int):
        atom = atoms.setdefault(abs(value), Bool(str(abs(value))))
        return atom if value > 0 else Not(atom)

    solver = Solver()
    for clause in clauses:
        if not clause:
            assert empty
            return
        solver.add(Or([lit(item) for item in clause]) if len(clause) > 1 else lit(clause[0]))
    assert (solver.check() != sat) == empty


class ResolveProofTask(BaseMathTask):
    TASK_TYPE = "resolve_proof"
    TASK_TYPES = ["empty", "length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.cancel = random.randint(0, 1)
        self.clauses, self.derived = resolution_trace(self.n, bool(self.cancel))
        self.length = len(self.derived[-1])
        self.empty = 1 if self.length == 0 else 0
        _sat_matches(self.clauses, bool(self.empty))
        self.answer = self.empty if self.task_type == "empty" else self.length
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(" ".join(str(lit) for lit in clause) if clause else "0" for clause in self.clauses)
        key = "s0" if self.task_type == "empty" else "s1"
        return texts.t(key, language, n=self.n, clauses=shown)

    def solve(self):
        steps = []
        for index, clause in enumerate(self.derived, 1):
            shown = " ".join(str(lit) for lit in clause) if clause else "0"
            steps.append(texts.t("s2", self.language, i=index, var=index, clause=shown, length=len(clause)))
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
