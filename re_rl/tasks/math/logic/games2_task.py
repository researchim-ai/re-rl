"""Игры с оптимальной стратегией: набор комбинаторных игр (мизерный Ним, игра
Витоффа, ход в игре вычитания, Chomp) и крестики-нолики (минимакс)."""

import math
import random
from functools import lru_cache
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_PHI = (1 + 5 ** 0.5) / 2


class _GameBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


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
        ru = language == "ru"
        if self.subtype == "misere_nim":
            heaps = ", ".join(map(str, self.heaps))
            return (("Мизерный Ним: кучки [" + heaps + "]. Игроки по очереди берут любое число камней "
                     "(≥1) из одной кучки. Тот, кто заберёт ПОСЛЕДНИЙ камень, ПРОИГРЫВАЕТ. Кто выигрывает "
                     "при оптимальной игре: первый или второй?") if ru else
                    ("Misère Nim: heaps [" + heaps + "]. Players alternately remove any number of stones "
                     "(≥1) from one heap. The player who takes the LAST stone LOSES. With optimal play, "
                     "who wins: first or second?"))
        if self.subtype == "wythoff":
            return ((f"Игра Витоффа: две кучки ({self.a}, {self.b}). За ход можно взять любое число камней "
                     f"из одной кучки ИЛИ поровну из обеих. Кто не может ходить — проигрывает. Кто выигрывает "
                     f"при оптимальной игре: первый или второй?") if ru else
                    (f"Wythoff's game: two heaps ({self.a}, {self.b}). A move takes any number from one heap "
                     f"OR the same number from both. A player who cannot move loses. With optimal play, who "
                     f"wins: first or second?"))
        if self.subtype == "chomp":
            return ((f"Игра Chomp: плитка шоколада {self.rows}×{self.cols}, левый нижний кусочек отравлен. "
                     f"За ход берут кусочек и всё, что выше и правее него. Кто съест отравленный — "
                     f"проигрывает. Кто выигрывает при оптимальной игре: первый или второй?") if ru else
                    (f"Chomp: a {self.rows}×{self.cols} chocolate bar, the bottom-left square is poisoned. "
                     f"A move eats a square and everything above-and-right of it. Whoever eats the poisoned "
                     f"square loses. With optimal play, who wins: first or second?"))
        moves = ", ".join(map(str, self.moves))
        return ((f"Из кучки в {self.heap} камней игроки по очереди берут количество из множества "
                 f"{{{moves}}}. Кто не может ходить — проигрывает. Сколько камней нужно взять первым ходом, "
                 f"чтобы выиграть при оптимальной игре? Если выигрышного хода нет, ответьте 0.") if ru else
                (f"From a heap of {self.heap} stones, players alternately remove an amount from the set "
                 f"{{{moves}}}. A player who cannot move loses. How many stones should the first move take "
                 f"to win with optimal play? If there is no winning move, answer 0."))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "subtraction_move":
            if self.is_winning:
                step = (f"Выигрышный ход ведёт в проигрышную для соперника позицию: взять {self.answer_move}." if ru else
                        f"A winning move leaves the opponent in a losing position: take {self.answer_move}.")
            else:
                step = ("Позиция проигрышна: выигрышного хода нет (ответ 0)." if ru else
                        "The position is losing: no winning move (answer 0).")
            self.solution_steps = [
                ("Помечаем позиции выигрышными/проигрышными снизу вверх." if ru else
                 "Label positions winning/losing from the bottom up."),
                step,
            ]
            self.final_answer = str(self.answer_move)
            return
        winner = ("первый" if self.first_wins else "второй") if ru else \
                 ("first" if self.first_wins else "second")
        self.solution_steps = [
            ("Применяем теорию игры для данной позиции." if ru else
             "Apply the game theory for this position."),
            (f"Выигрывает: {winner}." if ru else f"Winner: {winner}."),
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
            return U.verify_label(prediction, ["первый", "first"])
        return U.verify_label(prediction, ["второй", "second"])


class TicTacToeTask(_GameBase):
    TASK_TYPE = "tic_tac_toe"
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
        ru = language == "ru"
        head = (f"Крестики-нолики (3×3). Клетки нумеруются 1..9 слева направо, сверху вниз "
                f"(«.» — пусто). Ходит {self.player}. Позиция:\n{self._board_str()}\n" if ru else
                f"Tic-tac-toe (3×3). Cells are numbered 1..9 left-to-right, top-to-bottom "
                f"('.' empty). {self.player} to move. Position:\n{self._board_str()}\n")
        if self.subtype == "outcome":
            q = ("Каков исход при оптимальной игре обеих сторон? Ответьте: «первый (X)», «второй (O)» "
                 "или «ничья»." if ru else
                 "What is the outcome with optimal play by both sides? Answer: 'first (X)', 'second (O)', "
                 "or 'draw'.")
        else:
            q = (f"Укажите номер клетки (1..9) — оптимальный ход для {self.player}." if ru else
                 f"Give the cell number (1..9) of an optimal move for {self.player}.")
        return head + q

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "outcome":
            if self.value == 1:
                res = ("первый (X)" if ru else "first (X)")
            elif self.value == -1:
                res = ("второй (O)" if ru else "second (O)")
            else:
                res = ("ничья" if ru else "draw")
            self.solution_steps = [
                ("Полный перебор ходов (минимакс) с оптимальной игрой обеих сторон." if ru else
                 "Full move search (minimax) with optimal play by both sides."),
                (f"Исход: {res}." if ru else f"Outcome: {res}."),
            ]
            self.final_answer = res
        else:
            best = self._best_moves()
            self.solution_steps = [
                ("Оцениваем каждый ход минимаксом и берём оптимальный по значению." if ru else
                 "Evaluate each move by minimax and pick one optimal in value."),
                (f"Оптимальный ход: клетка {best[0] + 1}." if ru else
                 f"An optimal move: cell {best[0] + 1}."),
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
            "X": ["x", "крестики", "первый"],
            "O": ["o", "нолики", "второй"],
            "draw": ["ничья", "draw"],
        }
        cls = "X" if self.value == 1 else "O" if self.value == -1 else "draw"
        found = {k: U.verify_label(prediction, v) == 1.0 for k, v in syn.items()}
        if sum(found.values()) != 1:
            return 0.0
        return 1.0 if found[cls] else 0.0
