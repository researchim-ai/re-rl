"""Теория Шпрага–Гранди для импартиальных игр: число Гранди позиции (mex),
победитель суммы игр (XOR чисел Гранди), игра Kayles."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _mex(s):
    m = 0
    while m in s:
        m += 1
    return m


class SpragueGrundyTask(BaseMathTask):
    TASK_TYPE = "sprague_grundy"
    TASK_TYPES = ["grundy", "winner_sum", "kayles"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6, "heaps": 2}, 2: {"n": 8, "heaps": 2}, 3: {"n": 10, "heaps": 2},
        4: {"n": 12, "heaps": 3}, 5: {"n": 15, "heaps": 3}, 6: {"n": 18, "heaps": 3},
        7: {"n": 20, "heaps": 4}, 8: {"n": 24, "heaps": 4}, 9: {"n": 28, "heaps": 4},
        10: {"n": 32, "heaps": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nmax = int(p["n"])
        self.max_heaps = int(p["heaps"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _grundy_subtraction(self, moves, N):
        g = [0] * (N + 1)
        for n in range(1, N + 1):
            reach = {g[n - m] for m in moves if m <= n}
            g[n] = _mex(reach)
        return g

    def _kayles_grundy(self, N):
        g = [0] * (N + 1)
        for n in range(1, N + 1):
            reach = set()
            for i in range(n):          # снять 1 кеглю на позиции i -> ряды i и n-1-i
                reach.add(g[i] ^ g[n - 1 - i])
            for i in range(n - 1):      # снять 2 соседние -> ряды i и n-2-i
                reach.add(g[i] ^ g[n - 2 - i])
            g[n] = _mex(reach)
        return g

    def _build(self):
        if self.subtype == "kayles":
            self.n = random.randint(1, self.nmax)
            g = self._kayles_grundy(self.n)
            self.grundy = g[self.n]
            self.first_wins = self.grundy != 0
        elif self.subtype == "grundy":
            self.moves = sorted(random.sample(range(1, min(6, self.nmax)), k=random.randint(2, 3)))
            self.n = random.randint(1, self.nmax)
            g = self._grundy_subtraction(self.moves, self.n)
            self.grundy = g[self.n]
        else:  # winner_sum
            self.moves = sorted(random.sample(range(1, min(6, self.nmax)), k=random.randint(2, 3)))
            self.heaps = [random.randint(1, self.nmax) for _ in range(self.max_heaps)]
            g = self._grundy_subtraction(self.moves, max(self.heaps))
            self.xor = 0
            for h in self.heaps:
                self.xor ^= g[h]
            self.first_wins = self.xor != 0

    def _descr(self, language):
        if self.subtype == "kayles":
            return ((texts.t('s1', language, n=self.n)))
        if self.subtype == "grundy":
            moves = ", ".join(map(str, self.moves))
            return ((texts.t('s2', language, n=self.n, moves=moves, n_2=self.n)))
        moves = ", ".join(map(str, self.moves))
        heaps = ", ".join(map(str, self.heaps))
        return ((texts.t('s0', language, moves=moves, heaps=heaps)))

    def solve(self):
        if self.subtype in ("kayles", "grundy"):
            val = self.grundy
            self.solution_steps = [
                ((texts.t('s5', self.language))),
                ((texts.t('s6', self.language, val=val))),
            ]
            self.final_answer = str(val)
        else:
            winner = (texts.t('s3', self.language) if self.first_wins else texts.t('s4', self.language))
            self.solution_steps = [
                ((texts.t('s7', self.language))),
                ((texts.t('s8', self.language, xor=self.xor, winner=winner))),
            ]
            self.final_answer = winner

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype in ("kayles", "grundy"):
            return U.verify_int(prediction, int(self.grundy))
        if self.first_wins:
            return U.verify_label(prediction, [texts.t('s10', self.language), "first"])
        return U.verify_label(prediction, [texts.t('s9', self.language), "second"])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
