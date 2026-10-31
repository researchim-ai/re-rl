"""ShapleyValueTask — вектор Шепли для трёх игроков.

Значение игрока — среднее его маргинального вклада по всем 6 перестановкам.
Пустая коалиция стоит 0. Ответ — точная дробь со знаменателем, делящим 6.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from itertools import permutations
from typing import Any, ClassVar, Dict, FrozenSet

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def shapley(values: Dict[FrozenSet[int], int], player: int) -> Fraction:
    total = 0
    for perm in permutations((0, 1, 2)):
        coalition: FrozenSet[int] = frozenset()
        for p in perm:
            if p == player:
                total += values[coalition | frozenset([p])] - values[coalition]
                break
            coalition = coalition | frozenset([p])
    return Fraction(total, 6)


class ShapleyValueTask(BaseMathTask):
    TASK_TYPE = "shapley_value"
    TASK_TYPES = ["value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 3}, 2: {"v": 4}, 3: {"v": 5}, 4: {"v": 6}, 5: {"v": 6},
        6: {"v": 8}, 7: {"v": 8}, 8: {"v": 10}, 9: {"v": 12}, 10: {"v": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.vmax = int(p["v"])
        self.task_type = "value"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        base = [random.randint(0, self.vmax) for _ in range(3)]
        pair_bonus = [random.randint(0, self.vmax) for _ in range(3)]
        grand = random.randint(0, self.vmax)
        self.values: Dict[FrozenSet[int], int] = {frozenset(): 0}
        for i in range(3):
            self.values[frozenset([i])] = base[i]
        pairs = [(0, 1), (0, 2), (1, 2)]
        for bonus, (i, j) in zip(pair_bonus, pairs):
            self.values[frozenset([i, j])] = base[i] + base[j] + bonus
        self.values[frozenset([0, 1, 2])] = (
            self.values[frozenset([0, 1])] + base[2] + grand
        )
        self.player = random.randrange(3)
        self.answer = shapley(self.values, self.player)
        # Сумма Шепли равна v(всех).
        total = sum((shapley(self.values, i) for i in range(3)), Fraction(0))
        if total != self.values[frozenset([0, 1, 2])]:
            raise RuntimeError(texts.t('s2', self.language))

    def _v(self, key: str) -> int:
        mapping = {
            "1": frozenset([0]), "2": frozenset([1]), "3": frozenset([2]),
            "12": frozenset([0, 1]), "13": frozenset([0, 2]), "23": frozenset([1, 2]),
            "123": frozenset([0, 1, 2]),
        }
        return self.values[mapping[key]]

    def _descr(self, language):
        parts = ", ".join(f"v({name}) = {self._v(name)}" for name in ("1", "2", "3", "12", "13", "23", "123"))
        who = self.player + 1
        return ((texts.t('s0', language, parts=parts, who=who)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, shown=shown)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
