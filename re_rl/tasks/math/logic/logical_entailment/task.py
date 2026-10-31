"""LogicalEntailmentTask — семантическое следование в пропозициональной логике.

Даны посылки (формулы) и заключение. Нужно определить, следует ли заключение
из посылок (истинно во всех моделях, где истинны все посылки). Проверка — полным
перебором означиваний переменных.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class LogicalEntailmentTask(BaseMathTask):
    TASK_TYPE = "logical_entailment"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"vars": 2, "prem": 1, "depth": 2}, 2: {"vars": 2, "prem": 1, "depth": 2},
        3: {"vars": 2, "prem": 2, "depth": 2}, 4: {"vars": 3, "prem": 2, "depth": 2},
        5: {"vars": 3, "prem": 2, "depth": 3}, 6: {"vars": 3, "prem": 3, "depth": 3},
        7: {"vars": 4, "prem": 3, "depth": 3}, 8: {"vars": 4, "prem": 3, "depth": 3},
        9: {"vars": 4, "prem": 4, "depth": 4}, 10: {"vars": 5, "prem": 4, "depth": 4},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.nvars = int(preset["vars"])
        self.nprem = int(preset["prem"])
        self.max_depth = int(preset["depth"])
        self.augment = augment
        self.vars = ["p", "q", "r", "s", "t"][:self.nvars]
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _rand_formula(self, depth: int):
        if depth <= 0 or (depth < self.max_depth and random.random() < 0.35):
            return ("var", random.choice(self.vars))
        op = random.choice(["not", "and", "or", "imp", "iff"])
        if op == "not":
            return ("not", self._rand_formula(depth - 1))
        return (op, self._rand_formula(depth - 1), self._rand_formula(depth - 1))

    def _build(self):
        self.premises = [self._rand_formula(self.max_depth) for _ in range(self.nprem)]
        self.conclusion = self._rand_formula(self.max_depth)
        self._entails = self._check()

    def _eval(self, node, assign) -> bool:
        t = node[0]
        if t == "var":
            return assign[node[1]]
        if t == "not":
            return not self._eval(node[1], assign)
        a = self._eval(node[1], assign)
        b = self._eval(node[2], assign)
        if t == "and":
            return a and b
        if t == "or":
            return a or b
        if t == "imp":
            return (not a) or b
        return a == b  # iff

    def _check(self) -> bool:
        for bits in product([False, True], repeat=self.nvars):
            assign = dict(zip(self.vars, bits))
            if all(self._eval(p, assign) for p in self.premises):
                if not self._eval(self.conclusion, assign):
                    return False
        return True

    def _render(self, node) -> str:
        t = node[0]
        if t == "var":
            return node[1]
        if t == "not":
            return f"¬{self._render(node[1])}"
        sym = {"and": "∧", "or": "∨", "imp": "→", "iff": "↔"}[t]
        return f"({self._render(node[1])} {sym} {self._render(node[2])})"

    def _make_description(self, language: str) -> str:
        head = ((texts.t('s0', language)))
        body = "\n".join(f"{i + 1}) {self._render(p)}" for i, p in enumerate(self.premises))
        concl = ((texts.t('s1', language, v0=self._render(self.conclusion))))
        tail = ((texts.t('s2', language)))
        return head + body + concl + tail

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s5', self.language))),
            ((texts.t('s6', self.language) if self._entails else
               texts.t('s7', self.language))),
        ]
        self.final_answer = (texts.t('s3', self.language) if self._entails else texts.t('s4', self.language))

    def verify(self, prediction: str) -> float:
        self.solve()
        from re_rl.tasks.math.logic.proof_semantics import verify_boolean
        return verify_boolean(prediction,bool(self._entails))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
