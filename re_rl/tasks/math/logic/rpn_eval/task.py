"""Пошаговые алгоритмические задачи: вычисление ОПЗ (RPN), проверка баланса
скобок, трассировка сортировки (число инверсий / состояние после проходов)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.algo_sim_shared.base import _AlgoBase

class RPNEvalTask(_AlgoBase):
    TASK_TYPE = "rpn_eval"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "hi": 6}, 2: {"n": 3, "hi": 9}, 3: {"n": 4, "hi": 9}, 4: {"n": 4, "hi": 12},
        5: {"n": 5, "hi": 12}, 6: {"n": 5, "hi": 15}, 7: {"n": 6, "hi": 15}, 8: {"n": 6, "hi": 20},
        9: {"n": 7, "hi": 20}, 10: {"n": 8, "hi": 25},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.hi = int(p["n"]), int(p["hi"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # Строим случайное дерево, затем получаем постфиксную запись и значение.
        items = [([str(v)], v) for v in (random.randint(1, self.hi) for _ in range(self.n))]
        while len(items) > 1:
            i, j = random.sample(range(len(items)), 2)
            (ta, va), (tb, vb) = items[i], items[j]
            op = random.choice(["+", "-", "*"])
            val = va + vb if op == "+" else va - vb if op == "-" else va * vb
            tokens = ta + tb + [op]
            items = [it for idx, it in enumerate(items) if idx not in (i, j)]
            items.append((tokens, val))
        self.tokens, self._answer = items[0]

    def _descr(self, language):
        expr = " ".join(self.tokens)
        return ((texts.t('s0', language, expr=expr)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))
