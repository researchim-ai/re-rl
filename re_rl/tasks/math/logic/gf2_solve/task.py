"""Gf2SolveTask — треугольная система исключающего или.

Уравнение номера i определяет атом i через уже найденные более ранние атомы.
Сложение битов — исключающее или. z3 проверяет единственность решения.
Число атомов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from z3 import Bool, Not, Solver, Xor, is_true, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def gf2_trace(equations: Sequence[Tuple[Sequence[int], int]]) -> List[int]:
    values = []
    for earlier, rhs in equations:
        bit = rhs
        for index in earlier:
            bit ^= values[index]
        values.append(bit)
    return values


def _matches_z3(equations: Sequence[Tuple[Sequence[int], int]], values: Sequence[int]) -> None:
    atoms = [Bool(str(index)) for index in range(len(equations))]
    solver = Solver()
    for index, (earlier, rhs) in enumerate(equations):
        expr = atoms[index]
        for prev in earlier:
            expr = Xor(expr, atoms[prev])
        solver.add(expr if rhs else Not(expr))
    assert solver.check() == sat
    model = solver.model()
    for index, bit in enumerate(values):
        assert is_true(model.eval(atoms[index])) == bool(bit)


class Gf2SolveTask(BaseMathTask):
    TASK_TYPE = "gf2_solve"
    TASK_TYPES = ["bit", "weight"]

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
        hidden = [random.randint(0, 1) for _ in range(self.n)]
        self.equations: List[Tuple[List[int], int]] = []
        for index, bit in enumerate(hidden):
            earlier = [prev for prev in range(index) if random.random() < 0.5]
            rhs = bit
            for prev in earlier:
                rhs ^= hidden[prev]
            self.equations.append((earlier, rhs))
        self.values = gf2_trace(self.equations)
        assert self.values == hidden
        _matches_z3(self.equations, self.values)
        self.k = random.randint(1, self.n)
        self.bit = self.values[self.k - 1]
        self.weight = sum(self.values)
        self.answer = self.bit if self.task_type == "bit" else self.weight
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        lines = []
        for index, (earlier, rhs) in enumerate(self.equations, 1):
            if earlier:
                body = "+".join(str(item + 1) for item in earlier)
                lines.append(f"{index}={body}+{rhs}")
            else:
                lines.append(f"{index}={rhs}")
        key = "s0" if self.task_type == "bit" else "s1"
        return texts.t(key, language, n=self.n, equations=", ".join(lines), k=self.k)

    def solve(self):
        steps = []
        for index, ((earlier, rhs), bit) in enumerate(zip(self.equations, self.values), 1):
            body = "+".join(str(item + 1) for item in earlier) if earlier else "0"
            steps.append(texts.t("s2", self.language, i=index, body=body, rhs=rhs, bit=bit))
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
