"""KnightMovesTask — минимум ходов коня по пустой доске 8×8.

Расстояние считается обходом в ширину по 8 возможным ходам коня. На доске 8×8
граф коня связен, поэтому ответ всегда существует и не превосходит 6.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Square = Tuple[int, int]
_FILES = "abcdefgh"
_MOVES = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))


def square_name(sq: Square) -> str:
    f, r = sq
    return f"{_FILES[f]}{r + 1}"


def parse_square(name: str) -> Square:
    return _FILES.index(name[0]), int(name[1]) - 1


def knight_path(start: Square, goal: Square) -> List[Square]:
    """Кратчайший путь, включая начало и конец. Пустой список невозможен на 8×8."""
    if start == goal:
        return [start]
    prev: Dict[Square, Optional[Square]] = {start: None}
    q = deque([start])
    while q:
        f, r = q.popleft()
        for df, dr in _MOVES:
            nxt = (f + df, r + dr)
            nf, nr = nxt
            if not (0 <= nf < 8 and 0 <= nr < 8) or nxt in prev:
                continue
            prev[nxt] = (f, r)
            if nxt == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(prev[path[-1]])
                path.reverse()
                return path
            q.append(nxt)
    raise RuntimeError("конь не достиг цели на доске 8×8")


class KnightMovesTask(BaseMathTask):
    TASK_TYPE = "knight_moves"
    TASK_TYPES = ["min_moves"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"lo": 1, "hi": 1}, 2: {"lo": 1, "hi": 2}, 3: {"lo": 2, "hi": 2},
        4: {"lo": 2, "hi": 3}, 5: {"lo": 3, "hi": 3}, 6: {"lo": 3, "hi": 4},
        7: {"lo": 4, "hi": 4}, 8: {"lo": 4, "hi": 5}, 9: {"lo": 5, "hi": 6},
        10: {"lo": 6, "hi": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.lo = int(p["lo"])
        self.hi = int(p["hi"])
        self.task_type = "min_moves"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        for _ in range(200):
            start = (random.randrange(8), random.randrange(8))
            # Слои BFS до нужной дистанции.
            dist = {start: 0}
            q = deque([start])
            while q:
                f, r = q.popleft()
                for df, dr in _MOVES:
                    nxt = (f + df, r + dr)
                    nf, nr = nxt
                    if 0 <= nf < 8 and 0 <= nr < 8 and nxt not in dist:
                        dist[nxt] = dist[(f, r)] + 1
                        q.append(nxt)
            goals = [sq for sq, d in dist.items() if self.lo <= d <= self.hi]
            if goals:
                self.start = start
                self.goal = random.choice(goals)
                self.path = knight_path(self.start, self.goal)
                self.answer = len(self.path) - 1
                if not (self.lo <= self.answer <= self.hi):
                    raise RuntimeError("дистанция коня не совпала со слоем BFS")
                return
        raise RuntimeError("не удалось подобрать позицию коня")

    def _descr(self, language):
        ru = language == "ru"
        a, b = square_name(self.start), square_name(self.goal)
        return ((f"Пустая шахматная доска 8×8. Какое минимальное число ходов нужно коню, "
                 f"чтобы попасть с {a} на {b}?") if ru else
                (f"Empty 8×8 chessboard. What is the minimum number of knight moves from {a} to {b}?"))

    def solve(self):
        ru = self.language == "ru"
        shown = " -> ".join(square_name(sq) for sq in self.path)
        if ru:
            n = self.answer
            if n % 10 == 1 and n % 100 != 11:
                word = "ход"
            elif n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
                word = "хода"
            else:
                word = "ходов"
            head = f"Кратчайший путь ({n} {word}): {shown}."
        else:
            word = "move" if self.answer == 1 else "moves"
            head = f"Shortest path ({self.answer} {word}): {shown}."
        self.solution_steps = [
            head,
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
