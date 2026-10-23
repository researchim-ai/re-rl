"""RgsRankTask — ранг строки ограниченного роста.

Таблица считает, сколько строк продолжается из данной высоты. Ранг собирается по буквам.
Длина слова растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from sympy.combinatorics.partitions import RGS_rank

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def growth_table(length: int) -> Tuple[List[List[int]], List[Tuple[int, int, int]]]:
    size = length + 1
    table = [[0] * size for _ in range(size)]
    for column in range(size):
        table[0][column] = 1
    cells = []
    for row in range(1, size):
        for column in range(length):
            if column <= length - row:
                table[row][column] = (
                    column * table[row - 1][column] + table[row - 1][column + 1]
                )
            cells.append((row, column, table[row][column]))
    return table, cells


def rank_parts(word: List[int], table: List[List[int]]) -> Tuple[int, List[Tuple[int, int, int, int, int]]]:
    rank = 0
    parts = []
    length = len(word)
    for index in range(1, length):
        rest = length - index - 1
        seen = max(word[:index])
        part = table[rest][seen + 1] * word[index]
        rank += part
        parts.append((index, seen, rest, part, rank))
    return rank, parts


class RgsRankTask(BaseMathTask):
    TASK_TYPE = "rgs_rank"
    TASK_TYPES = ["rank", "part"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.word = [0]
        for _ in range(self.n - 1):
            self.word.append(random.randint(0, max(self.word) + 1))
        self.table, self.cells = growth_table(self.n)
        self.rank, self.parts = rank_parts(self.word, self.table)
        self.k = random.randint(1, self.n - 1)
        self.part = self.parts[self.k - 1][3]
        assert self.rank == int(RGS_rank(self.word))
        self.answer = self.rank if self.task_type == "rank" else self.part
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "rank" else "s1"
        word = ", ".join(str(item) for item in self.word)
        return texts.t(key, language, n=self.n, word=word, k=self.k, size=self.n + 1, last=self.n - 1)

    def solve(self):
        steps = [texts.t("s2", self.language, size=self.n + 1)]
        steps.extend(
            texts.t("s3", self.language, i=row, j=column, value=value)
            for row, column, value in self.cells
        )
        steps.extend(
            texts.t(
                "s4", self.language, i=index, seen=seen, rest=rest,
                letter=self.word[index], part=part, rank=rank,
            )
            for index, seen, rest, part, rank in self.parts
        )
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
