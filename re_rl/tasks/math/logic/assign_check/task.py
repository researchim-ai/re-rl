"""AssignCheckTask — проверка набора дизъюнктов на данном означивании.

Клауза истинна, если хотя бы один её литерал совпал с означиванием.
Число клауз растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def holds(literal: int, bits: Sequence[int]) -> bool:
    value = bits[abs(literal)]
    return value == 1 if literal > 0 else value == 0


def check_trace(clauses: Sequence[Sequence[int]], bits: Sequence[int]) -> List[Tuple[int, int, int]]:
    satisfied = 0
    first = 0
    trace = []
    for index, clause in enumerate(clauses, 1):
        ok = 1 if any(holds(literal, bits) for literal in clause) else 0
        if ok:
            satisfied += 1
        elif first == 0:
            first = index
        trace.append((ok, satisfied, first))
    return trace


class AssignCheckTask(BaseMathTask):
    TASK_TYPE = "assign_check"
    TASK_TYPES = ["sat", "fail"]

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
        self.bits = [0] + [random.randint(0, 1) for _ in range(self.n)]
        self.clauses = []
        for _ in range(self.n):
            width = random.randint(2, 3)
            lits = []
            for _ in range(width):
                var = random.randint(1, self.n)
                sign = random.choice((-1, 1))
                lits.append(sign * var)
            self.clauses.append(lits)
        self.trace = check_trace(self.clauses, self.bits)
        self.sat = self.trace[-1][1]
        self.fail = self.trace[-1][2]
        self.answer = self.sat if self.task_type == "sat" else self.fail
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits[1:])
        clauses = " | ".join(" ".join(str(lit) for lit in clause) for clause in self.clauses)
        key = "s0" if self.task_type == "sat" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, clauses=clauses)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, ok=ok, sat=sat, fail=fail)
            for index, (ok, sat, fail) in enumerate(self.trace, 1)
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
