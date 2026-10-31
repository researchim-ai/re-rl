"""Пошаговые алгоритмические задачи: вычисление ОПЗ (RPN), проверка баланса
скобок, трассировка сортировки (число инверсий / состояние после проходов)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.algo_sim_shared.base import _AlgoBase

class BalancedBracketsTask(_AlgoBase):
    TASK_TYPE = "balanced_brackets"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"pairs": 3, "kinds": 1}, 2: {"pairs": 4, "kinds": 1}, 3: {"pairs": 4, "kinds": 2},
        4: {"pairs": 5, "kinds": 2}, 5: {"pairs": 6, "kinds": 2}, 6: {"pairs": 6, "kinds": 3},
        7: {"pairs": 8, "kinds": 3}, 8: {"pairs": 9, "kinds": 3}, 9: {"pairs": 10, "kinds": 3},
        10: {"pairs": 12, "kinds": 3},
    }
    _PAIRS = [("(", ")"), ("[", "]"), ("{", "}")]

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.pairs = int(p["pairs"])
        self.kinds = int(p["kinds"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _random_balanced(self):
        opens = self._PAIRS[:self.kinds]
        s = []
        stack = []
        for _ in range(self.pairs * 2):
            if stack and (len(s) // 1) and random.random() < 0.5:
                s.append(stack.pop())
            else:
                o, c = random.choice(opens)
                s.append(o); stack.append(c)
        while stack:
            s.append(stack.pop())
        return "".join(s)

    def _build(self):
        self.balanced = random.random() < 0.5
        s = self._random_balanced()
        if not self.balanced:
            # портим: удаляем/меняем один символ
            s = list(s)
            i = random.randrange(len(s))
            allc = [c for pair in self._PAIRS[:self.kinds] for c in pair]
            s[i] = random.choice(allc)
            s = "".join(s)
            self.balanced = self._is_balanced(s)  # могло случайно остаться корректным
        self.s = s
        self._answer = self._is_balanced(s)

    def _is_balanced(self, s):
        close_to_open = {c: o for o, c in self._PAIRS}
        opens = {o for o, _ in self._PAIRS}
        stack = []
        for ch in s:
            if ch in opens:
                stack.append(ch)
            elif ch in close_to_open:
                if not stack or stack.pop() != close_to_open[ch]:
                    return False
        return not stack

    def _descr(self, language):
        return ((texts.t('s0', language, s=self.s)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language) if self._answer else texts.t('s5', self.language))),
        ]
        self.final_answer = (texts.t('s1', self.language) if self._answer else texts.t('s2', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))
