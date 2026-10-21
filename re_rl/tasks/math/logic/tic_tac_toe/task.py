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
from re_rl.tasks.math.logic.games2_shared.base import _GameBase

class TicTacToeTask(_GameBase):
    TASK_TYPE = texts.literal('literals.s10')
    TASK_TYPES = ["outcome", "best_move"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"moves": 6}, 2: {"moves": 6}, 3: {"moves": 5}, 4: {"moves": 5}, 5: {"moves": 4},
        6: {"moves": 4}, 7: {"moves": 3}, 8: {"moves": 3}, 9: {"moves": 2}, 10: {"moves": 2},
    }
    _WINS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.pre_moves = int(p["moves"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _winner(self, board):
        for a, b, c in self._WINS:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
        return None

    def _minimax(self, board, player):
        w = self._winner(board)
        if w == "X":
            return 1
        if w == "O":
            return -1
        if " " not in board:
            return 0
        moves = [i for i in range(9) if board[i] == " "]
        scores = []
        for i in moves:
            board[i] = player
            scores.append(self._minimax(board, "O" if player == "X" else "X"))
            board[i] = " "
        return max(scores) if player == "X" else min(scores)

    def _build(self):
        while True:
            board = [" "] * 9
            player = "X"
            ok = True
            for _ in range(self.pre_moves):
                empty = [i for i in range(9) if board[i] == " "]
                if not empty:
                    ok = False; break
                board[random.choice(empty)] = player
                if self._winner(board):
                    ok = False; break
                player = "O" if player == "X" else "X"
            if ok and self._winner(board) is None and " " in board:
                self.board = board
                self.player = player
                break
        self.value = self._minimax(self.board[:], self.player)

    def _board_str(self):
        rows = []
        for r in range(3):
            rows.append(" ".join(self.board[r * 3 + c] if self.board[r * 3 + c] != " " else "."
                                 for c in range(3)))
        return "\n".join(rows)

    def _descr(self, language):
        head = ((texts.t('s0', language, player=self.player, v1=self._board_str())))
        if self.subtype == "outcome":
            q = ((texts.t('s1', language)))
        else:
            q = ((texts.t('s2', language, player=self.player)))
        return head + q

    def solve(self):
        if self.subtype == "outcome":
            if self.value == 1:
                res = ((texts.t('s3', self.language)))
            elif self.value == -1:
                res = ((texts.t('s8', self.language)))
            else:
                res = ((texts.t('s9', self.language)))
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((texts.t('s5', self.language, res=res))),
            ]
            self.final_answer = res
        else:
            best = self._best_moves()
            self.solution_steps = [
                ((texts.t('s6', self.language))),
                ((texts.t('s7', self.language, v0=best[0] + 1))),
            ]
            self.final_answer = str(best[0] + 1)

    def _best_moves(self):
        moves = [i for i in range(9) if self.board[i] == " "]
        vals = {}
        for i in moves:
            self.board[i] = self.player
            vals[i] = self._minimax(self.board[:], "O" if self.player == "X" else "X")
            self.board[i] = " "
        best_val = max(vals.values()) if self.player == "X" else min(vals.values())
        return [i for i in moves if vals[i] == best_val]

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "best_move":
            m = U.last_int(prediction)
            if m is None or not (1 <= m <= 9) or self.board[m - 1] != " ":
                return 0.0
            self.board[m - 1] = self.player
            v = self._minimax(self.board[:], "O" if self.player == "X" else "X")
            self.board[m - 1] = " "
            best_val = self.value
            return 1.0 if v == best_val else 0.0
        syn = {
            "X": ["x", texts.t('s11', self.language), texts.t('s12', self.language)],
            "O": ["o", texts.t('s13', self.language), texts.t('s14', self.language)],
            "draw": [texts.t('s15', self.language), "draw"],
        }
        cls = "X" if self.value == 1 else "O" if self.value == -1 else "draw"
        found = {k: U.verify_label(prediction, v) == 1.0 for k, v in syn.items()}
        if sum(found.values()) != 1:
            return 0.0
        return 1.0 if found[cls] else 0.0
