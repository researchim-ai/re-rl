"""HavelHakimiTask — графична ли последовательность степеней.

Алгоритм Гавела–Хакими: сортируем по убыванию, вычитаем старшую степень
из следующих d членов. Сумма нечётная или степень больше числа оставшихся
вершин означает, что последовательность неграфична.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def is_graphic(seq: List[int]) -> bool:
    values = sorted(seq, reverse=True)
    if any(v < 0 for v in values):
        return False
    while values and values[0] == 0:
        values.pop(0)
    while values:
        values.sort(reverse=True)
        degree = values.pop(0)
        if degree == 0:
            return all(v == 0 for v in values)
        if degree > len(values):
            return False
        for i in range(degree):
            values[i] -= 1
            if values[i] < 0:
                return False
    return True


class HavelHakimiTask(BaseMathTask):
    TASK_TYPE = "havel_hakimi"
    TASK_TYPES = ["graphic"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "extra": 1}, 2: {"n": 4, "extra": 2}, 3: {"n": 5, "extra": 2},
        4: {"n": 5, "extra": 3}, 5: {"n": 6, "extra": 3}, 6: {"n": 6, "extra": 4},
        7: {"n": 7, "extra": 4}, 8: {"n": 8, "extra": 5}, 9: {"n": 8, "extra": 6},
        10: {"n": 9, "extra": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.extra = int(p["extra"])
        self.task_type = "graphic"
        self.augment = augment
        edges = set()
        for v in range(1, self.n):
            edges.add((v - 1, v))
        while len(edges) < self.n - 1 + self.extra:
            a, b = random.sample(range(self.n), 2)
            edges.add((min(a, b), max(a, b)))
        degree = [0] * self.n
        for a, b in edges:
            degree[a] += 1
            degree[b] += 1
        self.seq = degree[:]
        if random.random() < 0.45:
            i = random.randrange(self.n)
            self.seq[i] += 1
        random.shuffle(self.seq)
        self.graphic = is_graphic(self.seq)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = ", ".join(map(str, self.seq))
        return ((f"Последовательность целых чисел: {shown}. Является ли она последовательностью "
                 f"степеней простого неориентированного графа без петель? Ответьте да/нет.") if ru else
                (f"Integer sequence: {shown}. Is it the degree sequence of a simple undirected graph "
                 f"without loops? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        ans = ("да" if self.graphic else "нет") if ru else ("yes" if self.graphic else "no")
        step = (("Алгоритм Гавела–Хакими " + ("принимает" if self.graphic else "отвергает") + " последовательность.")
                if ru else
                ("The Havel–Hakimi algorithm " + ("accepts" if self.graphic else "rejects") + " the sequence."))
        self.solution_steps = [step, (f"Ответ: {ans}." if ru else f"Answer: {ans}.")]
        self.final_answer = ans

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, self.graphic)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
