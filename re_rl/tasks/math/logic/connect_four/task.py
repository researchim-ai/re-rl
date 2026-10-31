"""ConnectFourTask — «Четыре в ряд» на небольшом поле, решается минимаксом.

Фишки падают вниз по столбцам (гравитация). Игрок X ходит первым, O — вторым.
Побеждает выложивший K фишек подряд по горизонтали, вертикали или диагонали.

Подтипы:
- ``outcome``   — исход при оптимальной игре обеих сторон (первый/второй/ничья);
- ``best_move`` — номер столбца (1..W) оптимального хода для стороны, чья очередь.

Размер поля и K растут со сложностью, но число пустых клеток в предъявляемой
позиции ограничено, поэтому полный минимакс (с мемоизацией) быстр.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class ConnectFourTask(BaseMathTask):
    TASK_TYPE = "connect_four"
    TASK_TYPES = ["outcome", "best_move"]

    # (W, H, K, empties) — empties: число пустых клеток в предъявляемой позиции
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"w": 4, "h": 3, "k": 3, "empties": 4},
        2: {"w": 4, "h": 3, "k": 3, "empties": 5},
        3: {"w": 4, "h": 3, "k": 3, "empties": 6},
        4: {"w": 4, "h": 4, "k": 3, "empties": 6},
        5: {"w": 4, "h": 4, "k": 3, "empties": 7},
        6: {"w": 5, "h": 4, "k": 4, "empties": 7},
        7: {"w": 5, "h": 4, "k": 4, "empties": 8},
        8: {"w": 5, "h": 4, "k": 4, "empties": 8},
        9: {"w": 6, "h": 5, "k": 4, "empties": 9},
        10: {"w": 6, "h": 5, "k": 4, "empties": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.W, self.H, self.K = int(p["w"]), int(p["h"]), int(p["k"])
        self.empties = int(p["empties"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # --- игровая механика (столбцы снизу вверх) ---
    def _winner(self, cols: Tuple[Tuple[str, ...], ...]) -> Optional[str]:
        W, H, K = self.W, self.H, self.K
        grid = [[cols[c][r] if r < len(cols[c]) else " " for c in range(W)] for r in range(H)]

        def line(r0, c0, dr, dc):
            out = []
            r, c = r0, c0
            while 0 <= r < H and 0 <= c < W:
                out.append(grid[r][c]); r += dr; c += dc
            return out

        lines = []
        for r in range(H):
            lines.append([grid[r][c] for c in range(W)])
        for c in range(W):
            lines.append([grid[r][c] for r in range(H)])
        for r in range(H):
            for c in range(W):
                lines.append(line(r, c, 1, 1))
                lines.append(line(r, c, 1, -1))
        for ln in lines:
            run = 1
            for i in range(1, len(ln)):
                if ln[i] != " " and ln[i] == ln[i - 1]:
                    run += 1
                    if run >= K:
                        return ln[i]
                else:
                    run = 1
        return None

    def _valid(self, cols) -> List[int]:
        return [c for c in range(self.W) if len(cols[c]) < self.H]

    def _drop(self, cols, c, player):
        lst = list(cols)
        lst[c] = cols[c] + (player,)
        return tuple(lst)

    def _minimax(self, cols, player):
        key = (cols, player)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        w = self._winner(cols)
        if w == "X":
            res = 1
        elif w == "O":
            res = -1
        else:
            moves = self._valid(cols)
            if not moves:
                res = 0
            else:
                nxt = "O" if player == "X" else "X"
                vals = [self._minimax(self._drop(cols, c, player), nxt) for c in moves]
                res = max(vals) if player == "X" else min(vals)
        self._cache[key] = res
        return res

    def _build(self):
        self._cache: Dict = {}
        target_filled = self.W * self.H - self.empties
        while True:
            cols = tuple(() for _ in range(self.W))
            player = "X"
            ok = True
            for _ in range(target_filled):
                moves = self._valid(cols)
                if not moves:
                    ok = False; break
                cols = self._drop(cols, random.choice(moves), player)
                if self._winner(cols) is not None:
                    ok = False; break
                player = "O" if player == "X" else "X"
            if ok and self._winner(cols) is None and self._valid(cols):
                self.cols = cols
                self.player = player
                break
        self.value = self._minimax(self.cols, self.player)

    # --- рендер позиции текстом ---
    def _board_str(self):
        W, H = self.W, self.H
        rows = []
        for r in range(H - 1, -1, -1):
            rows.append(" ".join(self.cols[c][r] if r < len(self.cols[c]) else "."
                                 for c in range(W)))
        header = " ".join(str(c + 1) for c in range(W))
        return texts.t('s10', self.language, v0='\n'.join(rows), header=header)

    def _descr(self, language):
        who = self.player
        head = ((texts.t('s0', language, W=self.W, H=self.H, K=self.K, who=who, v4=self._board_str())))
        if self.task_type == "outcome":
            q = ((texts.t('s1', language)))
        else:
            q = ((texts.t('s2', language, W=self.W, who=who)))
        return head + q

    def _best_moves(self):
        moves = self._valid(self.cols)
        nxt = "O" if self.player == "X" else "X"
        vals = {c: self._minimax(self._drop(self.cols, c, self.player), nxt) for c in moves}
        best = max(vals.values()) if self.player == "X" else min(vals.values())
        return [c for c in moves if vals[c] == best]

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "outcome":
            if self.value == 1:
                res = ((texts.t('s3', self.language)))
            elif self.value == -1:
                res = ((texts.t('s8', self.language)))
            else:
                res = ((texts.t('s9', self.language)))
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((texts.t('s5', self.language, res=res)))]
            self.final_answer = res
        else:
            best = self._best_moves()
            self.solution_steps = [
                ((texts.t('s6', self.language))),
                ((texts.t('s7', self.language, v0=best[0] + 1)))]
            self.final_answer = str(best[0] + 1)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "best_move":
            m = U.last_int(prediction)
            if m is None or not (1 <= m <= self.W) or len(self.cols[m - 1]) >= self.H:
                return 0.0
            nxt = "O" if self.player == "X" else "X"
            v = self._minimax(self._drop(self.cols, m - 1, self.player), nxt)
            return 1.0 if v == self.value else 0.0
        syn = {
            "X": [texts.t('s11', self.language), "first", "x", texts.t('s12', self.language)],
            "O": [texts.t('s13', self.language), "second", "o", texts.t('s14', self.language)],
            "draw": [texts.t('s15', self.language), "draw"],
        }
        cls = "X" if self.value == 1 else "O" if self.value == -1 else "draw"
        found = {k: U.verify_label(prediction, v) == 1.0 for k, v in syn.items()}
        if sum(found.values()) != 1:
            return 0.0
        return 1.0 if found[cls] else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
