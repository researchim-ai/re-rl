"""GameTheoryOptimalTask — кто выигрывает при оптимальной игре.

Подтипы:
- nim: обычный Ним с несколькими кучками (теорема Шпрага–Гранди: выигрыш первого
  ⇔ XOR размеров кучек ≠ 0);
- subtraction: игра вычитания из одной кучки с разрешённым множеством ходов
  (динамика по проигрышным/выигрышным позициям).
Ответ: «первый» или «второй».
"""

import random
from functools import reduce
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GameTheoryOptimalTask(BaseMathTask):
    TASK_TYPE = "game_theory_optimal"
    TASK_TYPES = ["nim", "subtraction"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"heaps": 2, "hi": 5, "n": 12}, 2: {"heaps": 2, "hi": 7, "n": 16},
        3: {"heaps": 3, "hi": 7, "n": 20}, 4: {"heaps": 3, "hi": 9, "n": 25},
        5: {"heaps": 3, "hi": 12, "n": 30}, 6: {"heaps": 4, "hi": 12, "n": 40},
        7: {"heaps": 4, "hi": 15, "n": 50}, 8: {"heaps": 4, "hi": 20, "n": 60},
        9: {"heaps": 5, "hi": 20, "n": 80}, 10: {"heaps": 5, "hi": 25, "n": 100},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.max_heaps = int(preset["heaps"])
        self.hi = int(preset["hi"])
        self.n = int(preset["n"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "nim":
            self.heaps = [random.randint(1, self.hi) for _ in range(self.max_heaps)]
            self._first_wins = reduce(lambda a, b: a ^ b, self.heaps) != 0
        else:
            self.heap = random.randint(3, self.n)
            moves = sorted(random.sample(range(1, min(self.hi, self.heap) + 1),
                                         k=random.randint(2, 3)))
            self.moves = moves
            win = [False] * (self.heap + 1)  # win[k] — выигрывает ли ходящий из k
            for k in range(1, self.heap + 1):
                win[k] = any(m <= k and not win[k - m] for m in moves)
            self._first_wins = win[self.heap]

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        if self.subtype == "nim":
            heaps = ", ".join(str(h) for h in self.heaps)
            return (("Игра Ним. Есть кучки камней: [" + heaps + "]. Игроки ходят по очереди, "
                     "за ход берут любое число камней (≥1) из одной кучки. Кто не может ходить — "
                     "проигрывает. Кто выигрывает при оптимальной игре: первый или второй?") if ru else
                    ("Nim game. Heaps of stones: [" + heaps + "]. Players alternate turns, each turn "
                     "removing any number of stones (≥1) from a single heap. A player who cannot move "
                     "loses. With optimal play, who wins: first or second?"))
        moves = ", ".join(str(m) for m in self.moves)
        return ((f"Из кучки в {self.heap} камней игроки по очереди берут количество камней из "
                 f"множества {{{moves}}}. Кто не может сделать ход — проигрывает. Кто выигрывает при "
                 f"оптимальной игре: первый или второй?") if ru else
                (f"From a heap of {self.heap} stones, players alternately remove a number of stones "
                 f"from the set {{{moves}}}. A player who cannot move loses. With optimal play, who "
                 f"wins: first or second?"))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "nim":
            xor = reduce(lambda a, b: a ^ b, self.heaps)
            first = (f"XOR размеров кучек = {xor}. " if ru else f"XOR of heap sizes = {xor}. ")
            first += (("Он ненулевой — выигрывает первый." if self._first_wins else
                       "Он равен нулю — выигрывает второй.") if ru else
                      ("Non-zero — first player wins." if self._first_wins else
                       "Zero — second player wins."))
        else:
            first = ("Помечаем позиции: k проигрышна, если все ходы ведут в выигрышные. " if ru else
                     "Label positions: k is losing if every move leads to a winning one. ")
            first += (("Стартовая позиция выигрышна — первый." if self._first_wins else
                       "Стартовая позиция проигрышна — второй.") if ru else
                      ("Start position is winning — first." if self._first_wins else
                       "Start position is losing — second."))
        winner = ("первый" if self._first_wins else "второй") if ru else \
                 ("first" if self._first_wins else "second")
        self.solution_steps = [first, (f"Ответ: {winner}." if ru else f"Answer: {winner}.")]
        self.final_answer = winner

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self._first_wins:
            return U.verify_label(prediction, ["первый", "first"])
        return U.verify_label(prediction, ["второй", "second"])

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
