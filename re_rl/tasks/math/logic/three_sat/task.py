"""Формальная логика: классификация формул, подсчёт моделей, 3-SAT,
эквивалентность формул, квантифицированные булевы формулы (мини-QBF)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.formal_logic2_shared.base import _LogicBase

class ThreeSatTask(_LogicBase):
    TASK_TYPE = "three_sat"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 3, "c": 3}, 2: {"v": 3, "c": 4}, 3: {"v": 4, "c": 5}, 4: {"v": 4, "c": 6},
        5: {"v": 5, "c": 7}, 6: {"v": 5, "c": 9}, 7: {"v": 6, "c": 10}, 8: {"v": 6, "c": 12},
        9: {"v": 7, "c": 14}, 10: {"v": 7, "c": 16},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nv = int(p["v"])
        self.nc = int(p["c"])
        self.vars = [f"x{i+1}" for i in range(self.nv)]
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        hidden = [random.randint(0, 1) for _ in range(self.nv)]
        self.hidden = hidden
        self.assignment = hidden[:]
        self.clauses: List[List[Tuple[int, bool]]] = []  # (var_index, is_positive)
        for _ in range(self.nc):
            idxs = random.sample(range(self.nv), min(3, self.nv))
            clause = [(i, bool(random.getrandbits(1))) for i in idxs]
            if not any((hidden[i] == 1) == pos for i, pos in clause):
                i, _ = clause[0]  # чиним, чтобы клауза была истинна под hidden
                clause[0] = (i, hidden[i] == 1)
            self.clauses.append(clause)

    def _clause_str(self, clause):
        lits = [(f"{self.vars[i]}" if pos else f"¬{self.vars[i]}") for i, pos in clause]
        return "(" + " ∨ ".join(lits) + ")"

    def _descr(self, language):
        cnf = " ∧ ".join(self._clause_str(c) for c in self.clauses)
        return ((texts.t('s0', language, v0=', '.join(self.vars), cnf=cnf, v2=', '.join(self.vars))))

    def _satisfies(self, assign):
        for clause in self.clauses:
            if not any((assign[i] == 1) == pos for i, pos in clause):
                return False
        return True

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.assignment is None:
            self.final_answer = texts.t('unsatisfiable',self.language)
            self.solution_steps = [self.final_answer]
            return
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, v0=', '.join((f'{v}={b}' for v, b in zip(self.vars, self.assignment)))))),
        ]
        self.final_answer = " ".join(str(b) for b in self.assignment)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.assignment is None:
            return U.verify_label(prediction,[texts.t('unsatisfiable',self.language)])
        ints = U.parse_ints(prediction)
        bits = [x for x in ints if x in (0, 1)]
        if len(bits) < self.nv:
            return 0.0
        assign = bits[-self.nv:]
        return 1.0 if self._satisfies(assign) else 0.0
