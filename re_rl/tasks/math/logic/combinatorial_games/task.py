"""Игры с оптимальной стратегией: набор комбинаторных игр (мизерный Ним, игра
Витоффа, ход в игре вычитания, Chomp) и крестики-нолики (минимакс)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import math
import random
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.games2_shared.base import _GameBase, _PHI

class CombinatorialGamesTask(_GameBase):
    TASK_TYPE = "combinatorial_games"
    TASK_TYPES = ["misere_nim", "wythoff", "subtraction_move", "chomp"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"hi": 5, "heaps": 2}, 2: {"hi": 7, "heaps": 2}, 3: {"hi": 9, "heaps": 3},
        4: {"hi": 12, "heaps": 3}, 5: {"hi": 15, "heaps": 3}, 6: {"hi": 18, "heaps": 4},
        7: {"hi": 22, "heaps": 4}, 8: {"hi": 26, "heaps": 4}, 9: {"hi": 30, "heaps": 5},
        10: {"hi": 40, "heaps": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.hi = int(p["hi"])
        self.max_heaps = int(p["heaps"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "misere_nim":
            self.heaps = [random.randint(1, self.hi) for _ in range(self.max_heaps)]
            xor = 0
            for h in self.heaps:
                xor ^= h
            if max(self.heaps) <= 1:
                self.first_wins = (len(self.heaps) % 2 == 0)
            else:
                self.first_wins = (xor != 0)
        elif self.subtype == "wythoff":
            self.a = random.randint(0, self.hi)
            self.b = random.randint(0, self.hi)
            lo, hi = min(self.a, self.b), max(self.a, self.b)
            is_p = lo == int((hi - lo) * _PHI)
            self.first_wins = not is_p
        elif self.subtype == "chomp":
            self.rows = random.randint(1, max(2, self.hi // 4))
            self.cols = random.randint(1, max(2, self.hi // 4))
            self.first_wins = not (self.rows == 1 and self.cols == 1)
        else:  # subtraction_move
            self.heap = random.randint(4, self.hi + 4)
            self.moves = sorted(random.sample(range(1, min(self.hi, self.heap) + 1),
                                              k=random.randint(2, 3)))
            win = [False] * (self.heap + 1)
            for k in range(1, self.heap + 1):
                win[k] = any(m <= k and not win[k - m] for m in self.moves)
            self.win = win
            self.is_winning = win[self.heap]
            if self.is_winning:
                self.answer_move = next(m for m in self.moves if m <= self.heap and not win[self.heap - m])
            else:
                self.answer_move = 0

    def _descr(self, language):
        if self.subtype == "misere_nim":
            heaps = ", ".join(map(str, self.heaps))
            return ((texts.t('s3', language, heaps=heaps)))
        if self.subtype == "wythoff":
            return ((texts.t('s4', language, a=self.a, b=self.b)))
        if self.subtype == "chomp":
            return ((texts.t('s5', language, rows=self.rows, cols=self.cols)))
        moves = ", ".join(map(str, self.moves))
        return ((texts.t('s0', language, heap=self.heap, moves=moves)))

    def solve(self):
        if self.subtype == "subtraction_move":
            if self.is_winning:
                step = ((texts.t('s8', self.language, answer_move=self.answer_move)))
            else:
                step = ((texts.t('s9', self.language)))
            self.solution_steps = [
                ((texts.t('s10', self.language))),
                step,
            ]
            self.final_answer = str(self.answer_move)
            return
        winner = (texts.t('s1', self.language) if self.first_wins else texts.t('s2', self.language))
        self.solution_steps = [
            ((texts.t('s6', self.language))),
            ((texts.t('s7', self.language, winner=winner))),
        ]
        self.final_answer = winner

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "subtraction_move":
            m = U.last_int(prediction)
            if m is None:
                return 0.0
            if not self.is_winning:
                return 1.0 if m == 0 else 0.0
            return 1.0 if (m in self.moves and m <= self.heap and not self.win[self.heap - m]) else 0.0
        if self.first_wins:
            return U.verify_label(prediction, [texts.t('s12', self.language), "first"])
        return U.verify_label(prediction, [texts.t('s11', self.language), "second"])
