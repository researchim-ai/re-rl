"""UnitPropTask — вывод по однопосылочным импликациям.

Сначала известен атом 1. Правило «если источник равен нужному биту, вывод получает целевой бит» применяется по порядку.
Неизвестный атом остаётся неизвестным. z3 проверяет, что бит действительно вынужден.
Число атомов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from z3 import Bool, Not, Or, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Rule = Tuple[int, int, int, int]


def unit_trace(start: int, rules: Sequence[Rule]) -> Tuple[List[Tuple[int, int]], List[Optional[int]]]:
    size = len(rules) + 1
    values: List[Optional[int]] = [None] * (size + 1)
    values[1] = start
    trues = 1 if start == 1 else 0
    trace = [(start, trues)]
    for source, need, _dest, target in rules:
        if values[source] == need:
            values[_dest] = target
        if values[_dest] == 1:
            trues += 1
        shown = 2 if values[_dest] is None else values[_dest]
        trace.append((shown, trues))
    return trace, values


def _forced_by_z3(start: int, rules: Sequence[Rule], values: Sequence[Optional[int]]) -> None:
    size = len(rules) + 1
    atoms = [None] + [Bool(str(index)) for index in range(1, size + 1)]
    base = Solver()
    base.add(atoms[1] if start else Not(atoms[1]))
    for source, need, dest, target in rules:
        premise = atoms[source] if need else Not(atoms[source])
        conclusion = atoms[dest] if target else Not(atoms[dest])
        base.add(Or(Not(premise), conclusion))
    for index in range(1, size + 1):
        yes = Solver()
        yes.add(base.assertions())
        yes.add(atoms[index])
        no = Solver()
        no.add(base.assertions())
        no.add(Not(atoms[index]))
        can_yes = yes.check() == sat
        can_no = no.check() == sat
        if values[index] is None:
            assert can_yes and can_no
        elif values[index] == 1:
            assert can_yes and not can_no
        else:
            assert can_no and not can_yes


class UnitPropTask(BaseMathTask):
    TASK_TYPE = "unit_prop"
    TASK_TYPES = ["bit", "trues"]

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
        self.start = random.randint(0, 1)
        self.rules: List[Rule] = []
        for dest in range(2, self.n + 1):
            source = random.randint(1, dest - 1)
            need = random.randint(0, 1)
            target = random.randint(0, 1)
            self.rules.append((source, need, dest, target))
        self.trace, self.values = unit_trace(self.start, self.rules)
        _forced_by_z3(self.start, self.rules, self.values)
        self.k = random.randint(1, self.n)
        self.bit = 2 if self.values[self.k] is None else self.values[self.k]
        self.trues = self.trace[-1][1]
        self.answer = self.bit if self.task_type == "bit" else self.trues
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rules = ", ".join(
            f"{source}={need}->{dest}={target}" for source, need, dest, target in self.rules
        )
        key = "s0" if self.task_type == "bit" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, rules=rules, k=self.k)

    def solve(self):
        steps = [texts.t("s2", self.language, i=1, shown=self.trace[0][0], trues=self.trace[0][1])]
        for index, ((source, need, dest, target), (shown, trues)) in enumerate(
            zip(self.rules, self.trace[1:]), 2
        ):
            steps.append(texts.t(
                "s3", self.language, i=index, source=source, need=need,
                dest=dest, target=target, shown=shown, trues=trues,
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
