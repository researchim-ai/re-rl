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

class LogicalEquivalenceTask(_LogicBase):
    TASK_TYPE = "logical_equivalence"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 2, "d": 2}, 2: {"v": 2, "d": 2}, 3: {"v": 2, "d": 3}, 4: {"v": 3, "d": 3},
        5: {"v": 3, "d": 3}, 6: {"v": 3, "d": 4}, 7: {"v": 4, "d": 4}, 8: {"v": 4, "d": 4},
        9: {"v": 4, "d": 5}, 10: {"v": 5, "d": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vars = _VARS[:int(p["v"])]
        self.max_depth = int(p["d"])
        self.augment = augment
        self.f1 = _rand_formula(self.vars, self.max_depth, self.max_depth)
        # С вероятностью 50% делаем вторую формулу эквивалентной (лёгкое преобразование).
        if random.random() < 0.5:
            self.f2 = self._maybe_transform(self.f1)
        else:
            self.f2 = _rand_formula(self.vars, self.max_depth, self.max_depth)
        self._answer = all(_eval(self.f1, dict(zip(self.vars, bits))) ==
                           _eval(self.f2, dict(zip(self.vars, bits)))
                           for bits in product([False, True], repeat=len(self.vars)))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _maybe_transform(self, node):
        # двойное отрицание / коммутативность — сохраняют эквивалентность
        choice = random.random()
        if choice < 0.4:
            return ("not", ("not", node))
        if choice < 0.7 and node[0] in ("and", "or"):
            return (node[0], node[2], node[1])
        return node

    def _descr(self, language):
        return ((texts.t('s0', language, v0=', '.join(self.vars), v1=_render(self.f1), v2=_render(self.f2))))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language) if self._answer else
               texts.t('s5', self.language))),
        ]
        self.final_answer = (texts.t('s1', self.language) if self._answer else texts.t('s2', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
