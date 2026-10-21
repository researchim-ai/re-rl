"""GameTheoryOptimalTask — кто выигрывает при оптимальной игре.

Подтипы:
- nim: обычный Ним с несколькими кучками (теорема Шпрага–Гранди: выигрыш первого
  ⇔ XOR размеров кучек ≠ 0);
- subtraction: игра вычитания из одной кучки с разрешённым множеством ходов
  (динамика по проигрышным/выигрышным позициям).
Ответ: «первый» или «второй».
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from functools import reduce
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class GameTheoryOptimalTask(BaseMathTask):
    TASK_TYPE = texts.literal('literals.s10')
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
        if self.subtype == "nim":
            heaps = ", ".join(str(h) for h in self.heaps)
            return ((texts.t('s3', language, heaps=heaps)))
        moves = ", ".join(str(m) for m in self.moves)
        return ((texts.t('s0', language, heap=self.heap, moves=moves)))

    def solve(self):
        if self.subtype == "nim":
            xor = reduce(lambda a, b: a ^ b, self.heaps)
            first = ((texts.t('s4', self.language, xor=xor)))
            first += ((texts.t('s5', self.language) if self._first_wins else
                       texts.t('s6', self.language)))
        else:
            first = ((texts.t('s7', self.language)))
            first += ((texts.t('s8', self.language) if self._first_wins else
                       texts.t('s9', self.language)))
        winner = (texts.t('s1', self.language) if self._first_wins else texts.t('s2', self.language))
        self.solution_steps = [first, ((texts.common('answer_line', self.language, answer=winner)))]
        self.final_answer = winner

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self._first_wins:
            return U.verify_label(prediction, [texts.t('s12', self.language), "first"])
        return U.verify_label(prediction, [texts.t('s11', self.language), "second"])

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
