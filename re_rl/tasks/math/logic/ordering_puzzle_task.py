"""OrderingPuzzleTask — дедукция полного порядка из подсказок.

Несколько объектов расставлены в ряд (позиции 1..n). По набору подсказок
(«X раньше Y», «X сразу перед Y», «X на позиции k», «X первый/последний»)
нужно восстановить единственный порядок. Уникальность гарантируется перебором
всех перестановок при генерации.
"""

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_NAMES = ["Анна", "Борис", "Вера", "Глеб", "Дина", "Егор", "Жанна", "Игорь"]
_NAMES_EN = ["Anna", "Boris", "Vera", "Gleb", "Dina", "Egor", "Jane", "Igor"]


class OrderingPuzzleTask(BaseMathTask):
    TASK_TYPE = "ordering_puzzle"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 6}, 10: {"n": 7},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.augment = augment
        self.names = (_NAMES if language == "ru" else _NAMES_EN)[:self.n]
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _clue_holds(self, order: tuple, clue) -> bool:
        pos = {name: i for i, name in enumerate(order)}
        kind = clue[0]
        if kind == "before":
            return pos[clue[1]] < pos[clue[2]]
        if kind == "immediate":
            return pos[clue[2]] - pos[clue[1]] == 1
        if kind == "at":
            return pos[clue[1]] == clue[2]
        if kind == "first":
            return pos[clue[1]] == 0
        if kind == "last":
            return pos[clue[1]] == self.n - 1
        return False

    def _count_solutions(self, clues) -> int:
        cnt = 0
        for perm in permutations(self.names):
            if all(self._clue_holds(perm, c) for c in clues):
                cnt += 1
                if cnt > 1:
                    return cnt
        return cnt

    def _build(self):
        order = self.names[:]
        random.shuffle(order)
        self.true_order: List[str] = order
        pos = {name: i for i, name in enumerate(order)}

        candidates = []
        for i in range(self.n):
            for j in range(self.n):
                if i != j and pos[order[i]] < pos[order[j]]:
                    candidates.append(("before", order[i], order[j]))
        for i in range(self.n - 1):
            candidates.append(("immediate", order[i], order[i + 1]))
        candidates.append(("first", order[0]))
        candidates.append(("last", order[-1]))
        random.shuffle(candidates)

        # Жадно набираем минимальный набор подсказок до уникальности.
        clues = []
        for c in candidates:
            clues.append(c)
            if self._count_solutions(clues) == 1:
                break
        if self._count_solutions(clues) != 1:  # страховка
            clues = [("at", name, pos[name]) for name in order]
        # Удаляем избыточные подсказки.
        pruned = clues[:]
        for c in clues:
            trial = [x for x in pruned if x is not c]
            if self._count_solutions(trial) == 1:
                pruned = trial
        random.shuffle(pruned)
        self.clues = pruned

    def _clue_text(self, clue, ru: bool) -> str:
        k = clue[0]
        if k == "before":
            return (f"{clue[1]} стоит где-то раньше, чем {clue[2]}." if ru else
                    f"{clue[1]} is somewhere before {clue[2]}.")
        if k == "immediate":
            return (f"{clue[1]} стоит непосредственно перед {clue[2]}." if ru else
                    f"{clue[1]} is immediately before {clue[2]}.")
        if k == "at":
            return (f"{clue[1]} стоит на позиции {clue[2] + 1}." if ru else
                    f"{clue[1]} is at position {clue[2] + 1}.")
        if k == "first":
            return (f"{clue[1]} стоит первым." if ru else f"{clue[1]} is first.")
        return (f"{clue[1]} стоит последним." if ru else f"{clue[1]} is last.")

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        head = (f"{self.n} человек стоят в ряд на позициях с 1 по {self.n}: {', '.join(self.names)}.\n"
                f"Подсказки:\n" if ru else
                f"{self.n} people stand in a row at positions 1..{self.n}: {', '.join(self.names)}.\n"
                f"Clues:\n")
        body = "\n".join(f"- {self._clue_text(c, ru)}" for c in self.clues)
        tail = ("\nВосстановите порядок от первого к последнему (перечислите имена по порядку)."
                if ru else
                "\nReconstruct the order from first to last (list the names in order).")
        return head + body + tail

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Комбинируем подсказки, сужая возможные позиции каждого объекта." if ru else
             "Combine the clues to narrow down each object's possible positions."),
            ((f"Единственный порядок: {' → '.join(self.true_order)}.") if ru else
             (f"The unique order: {' → '.join(self.true_order)}.")),
        ]
        self.final_answer = ", ".join(self.true_order)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        seq = U.extract_name_sequence(prediction, self.names)
        return 1.0 if seq == self.true_order else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
