"""Игра в «пятнашки» (sliding puzzle).

Подтипы:
- ``solvable``  — разрешима ли данная расстановка (по чётности инверсий), да/нет;
- ``min_moves`` — минимальное число ходов до цели (поиск A* с манхэттенской эвристикой,
  поле 3×3).

Масштаб: размер поля и глубина перемешивания.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import heapq
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U


class SlidingPuzzleTask(BaseMathTask):
    TASK_TYPE = "sliding_puzzle"
    TASK_TYPES = ["solvable", "min_moves"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "scramble": 4}, 2: {"n": 3, "scramble": 6},
        3: {"n": 3, "scramble": 8}, 4: {"n": 3, "scramble": 10},
        5: {"n": 3, "scramble": 12}, 6: {"n": 3, "scramble": 14},
        7: {"n": 3, "scramble": 16}, 8: {"n": 3, "scramble": 18},
        9: {"n": 3, "scramble": 20}, 10: {"n": 3, "scramble": 22},
    }
    # Для solvable размер поля масштабируется отдельно.
    SOLVABLE_N: ClassVar[Dict[int, int]] = {d: (3 if d <= 5 else 4) for d in range(1, 11)}

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        if self.task_type not in self.TASK_TYPES:
            raise ValueError("invalid_subtype")
        self.scramble = int(p["scramble"])
        self.difficulty = difficulty if difficulty else 5
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.task_type == "solvable":
            self.n = self.SOLVABLE_N.get(int(self.difficulty), 3)
            perm = list(range(self.n * self.n))
            random.shuffle(perm)
            self.board = tuple(perm)
            self.answer_bool = self._is_solvable(self.board, self.n)
        else:
            self.n = 3
            self.board = self._scramble(self.scramble)
            self.answer_int = self._astar(self.board)

    # --- разрешимость по чётности инверсий ---
    @staticmethod
    def _inversions(board: Tuple[int, ...]) -> int:
        tiles = [x for x in board if x != 0]
        inv = 0
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    inv += 1
        return inv

    def _is_solvable(self, board: Tuple[int, ...], n: int) -> bool:
        inv = self._inversions(board)
        if n % 2 == 1:
            return inv % 2 == 0
        blank_row_from_bottom = n - (board.index(0) // n)
        return (inv + blank_row_from_bottom) % 2 == 1

    # --- перемешивание из цели (гарантированно разрешимо) ---
    def _goal(self) -> Tuple[int, ...]:
        return tuple(list(range(1, self.n * self.n)) + [0])

    def _neighbors(self, board: Tuple[int, ...]):
        n = self.n
        z = board.index(0)
        r, c = divmod(z, n)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                nz = nr * n + nc
                lst = list(board)
                lst[z], lst[nz] = lst[nz], lst[z]
                yield tuple(lst)

    def _scramble(self, k: int) -> Tuple[int, ...]:
        board = self._goal()
        prev = None
        for _ in range(k):
            nbrs = [b for b in self._neighbors(board) if b != prev]
            prev = board
            board = random.choice(nbrs)
        return board

    def _manhattan(self, board: Tuple[int, ...]) -> int:
        n = self.n
        total = 0
        for idx, tile in enumerate(board):
            if tile == 0:
                continue
            gr, gc = divmod(tile - 1, n)
            r, c = divmod(idx, n)
            total += abs(gr - r) + abs(gc - c)
        return total

    def _astar(self, start: Tuple[int, ...]) -> int:
        goal = self._goal()
        if start == goal:
            return 0
        openh = [(self._manhattan(start), 0, start)]
        best = {start: 0}
        while openh:
            f, g, board = heapq.heappop(openh)
            if board == goal:
                return g
            if g > best.get(board, 1 << 30):
                continue
            for nb in self._neighbors(board):
                ng = g + 1
                if ng < best.get(nb, 1 << 30):
                    best[nb] = ng
                    heapq.heappush(openh, (ng + self._manhattan(nb), ng, nb))
        return -1

    def _fmt(self, board: Tuple[int, ...]) -> str:
        n = self.n
        rows = []
        for r in range(n):
            cells = []
            for c in range(n):
                v = board[r * n + c]
                cells.append("_" if v == 0 else str(v))
            rows.append(" ".join(f"{x:>2}" for x in cells))
        return "\n".join(rows)

    def _descr(self, language):
        grid = self._fmt(self.board)
        goal = self._fmt(self._goal())
        if self.task_type == "solvable":
            return ((texts.t('s1', language, n=self.n, n_2=self.n, grid=grid, v3=self.n * self.n - 1, goal=goal)))
        return ((texts.t('s0', language, grid=grid, goal=goal)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "solvable":
            inv = self._inversions(self.board)
            self.solution_steps = [
                ((texts.t('s4', self.language, inv=inv))),
                ((texts.t('s5', self.language)))]
            self.final_answer = (texts.t('s2', self.language) if self.answer_bool else texts.t('s3', self.language))
        else:
            self.solution_steps = [
                ((texts.t('s6', self.language))),
                ((texts.t('s7', self.language, answer_int=self.answer_int)))]
            self.final_answer = str(self.answer_int)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "solvable":
            return U.verify_bool(prediction, self.answer_bool)
        return U.verify_int(prediction, int(self.answer_int))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
