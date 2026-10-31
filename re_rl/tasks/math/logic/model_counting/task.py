"""Формальная логика: классификация формул, подсчёт моделей, 3-SAT,
эквивалентность формул, квантифицированные булевы формулы (мини-QBF)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.formal_logic2_shared.base import _LogicBase, _VARS, _eval, _rand_formula, _render

class ModelCountingTask(_LogicBase):
    TASK_TYPE = "model_counting"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 3}, 3: {"v": 3, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 4}, 6: {"v": 4, "d": 4}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 5},
        9: {"v": 5, "d": 5}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.formula = _rand_formula(self.vars, self.max_depth, self.max_depth)
        self._answer = sum(1 for bits in product([False, True], repeat=len(self.vars))
                           if _eval(self.formula, dict(zip(self.vars, bits))))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, v0=', '.join(self.vars), v1=_render(self.formula))))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, v0=2 ** len(self.vars)))),
            ((texts.t('s2', self.language, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
