"""Пошаговые алгоритмические задачи: вычисление ОПЗ (RPN), проверка баланса
скобок, трассировка сортировки (число инверсий / состояние после проходов)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.algo_sim_shared.base import _AlgoBase

class SortingTraceTask(_AlgoBase):
    TASK_TYPE = "sorting_trace"
    TASK_TYPES = ["inversions", "bubble_pass"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 7},
        6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10}, 9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.subtype = subtype or kwargs.get("task_type") or random.choice(self.TASK_TYPES)
        self.augment = augment
        self.arr = random.sample(range(1, self.n * 3), self.n)
        if self.subtype == "inversions":
            self._answer = sum(1 for i in range(self.n) for j in range(i + 1, self.n)
                               if self.arr[i] > self.arr[j])
        else:
            self.k = random.randint(1, max(1, self.n - 2))
            self.result = self._bubble_passes(self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _bubble_passes(self, k):
        a = self.arr[:]
        for _ in range(k):
            for i in range(len(a) - 1):
                if a[i] > a[i + 1]:
                    a[i], a[i + 1] = a[i + 1], a[i]
        return a

    def _descr(self, language):
        arr = ", ".join(map(str, self.arr))
        if self.subtype == "inversions":
            return ((texts.t('s1', language, arr=arr)))
        return ((texts.t('s0', language, arr=arr, k=self.k)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.subtype == "inversions":
            self.solution_steps = [
                ((texts.t('s2', self.language))),
                ((texts.t('s3', self.language, _answer=self._answer))),
            ]
            self.final_answer = str(self._answer)
        else:
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((texts.t('s5', self.language, k=self.k, v1=', '.join(map(str, self.result))))),
            ]
            self.final_answer = " ".join(map(str, self.result))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "inversions":
            return U.verify_int(prediction, int(self._answer))
        return U.verify_int_sequence(prediction, self.result)
