"""Теория Шпрага–Гранди для импартиальных игр: число Гранди позиции (mex),
победитель суммы игр (XOR чисел Гранди), игра Kayles."""

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
        ru = language == "ru"
        if self.subtype == "kayles":
            return ((f"Игра Kayles: ряд из {self.n} кеглей. За ход сбивают одну кеглю ИЛИ две соседние, "
                     f"ряд может разбиваться на части. Кто не может ходить — проигрывает. Чему равно число "
                     f"Гранди этой позиции?") if ru else
                    (f"Kayles: a row of {self.n} pins. A move knocks down one pin OR two adjacent pins, "
                     f"possibly splitting the row. A player who cannot move loses. What is the Grundy value "
                     f"of this position?"))
        if self.subtype == "grundy":
            moves = ", ".join(map(str, self.moves))
            return ((f"Игра вычитания: из кучки в {self.n} камней за ход берут количество из множества "
                     f"{{{moves}}}. Кто не может ходить — проигрывает. Чему равно число Гранди позиции "
                     f"с {self.n} камнями?") if ru else
                    (f"Subtraction game: from a heap of {self.n} stones a move removes an amount from "
                     f"{{{moves}}}. A player who cannot move loses. What is the Grundy value of the "
                     f"position with {self.n} stones?"))
        moves = ", ".join(map(str, self.moves))
        heaps = ", ".join(map(str, self.heaps))
        return ((f"Сумма игр вычитания с множеством ходов {{{moves}}}. Кучки: [{heaps}]. За ход берут "
                 f"камни из ОДНОЙ кучки (разрешённое количество). Кто не может ходить — проигрывает. Кто "
                 f"выигрывает при оптимальной игре: первый или второй?") if ru else
                (f"Sum of subtraction games with move set {{{moves}}}. Heaps: [{heaps}]. A move removes "
                 f"(an allowed amount of) stones from ONE heap. A player who cannot move loses. With "
                 f"optimal play, who wins: first or second?"))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype in ("kayles", "grundy"):
            val = self.grundy
            self.solution_steps = [
                ("Число Гранди = mex значений Гранди достижимых позиций." if ru else
                 "The Grundy value = mex of the Grundy values of reachable positions."),
                (f"Число Гранди = {val}." if ru else f"Grundy value = {val}."),
            ]
            self.final_answer = str(val)
        else:
            winner = ("первый" if self.first_wins else "второй") if ru else \
                     ("first" if self.first_wins else "second")
            self.solution_steps = [
                ("XOR чисел Гранди кучек: не ноль — выигрывает первый, ноль — второй." if ru else
                 "XOR of the heaps' Grundy values: nonzero → first wins, zero → second."),
                (f"XOR = {self.xor} ⇒ выигрывает {winner}." if ru else
                 f"XOR = {self.xor} ⇒ {winner} wins."),
            ]
            self.final_answer = winner

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype in ("kayles", "grundy"):
            return U.verify_int(prediction, int(self.grundy))
        if self.first_wins:
            return U.verify_label(prediction, ["первый", "first"])
        return U.verify_label(prediction, ["второй", "second"])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
