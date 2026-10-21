"""BinarySearchTask — двоичный поиск в отсортированном массиве.

Границы включительные, середина mid = (lo + hi) // 2. Цель всегда есть в массиве.
Сравнение — одно обращение к элементу середины, включая удачное.

Подтипы: ``index`` (с нуля) и ``comparisons``.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def binary_search(arr: List[int], target: int) -> Tuple[int, int, List[int]]:
    lo, hi = 0, len(arr) - 1
    mids: List[int] = []
    while lo <= hi:
        mid = (lo + hi) // 2
        mids.append(mid)
        if arr[mid] == target:
            return mid, len(mids), mids
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    raise RuntimeError("цель отсутствует в массиве")


class BinarySearchTask(BaseMathTask):
    TASK_TYPE = "binary_search"
    TASK_TYPES = ["index", "comparisons"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5}, 2: {"n": 6}, 3: {"n": 7}, 4: {"n": 8}, 5: {"n": 9},
        6: {"n": 11}, 7: {"n": 13}, 8: {"n": 15}, 9: {"n": 17}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        start = random.randint(-5, 5)
        gap = 1
        self.arr = [start + i * gap for i in range(self.n)]
        # Иногда разрежаем, сохраняя строгий рост.
        if self.n >= 6 and random.random() < 0.5:
            self.arr = sorted(random.sample(range(start, start + self.n * 3), self.n))
        self.target = random.choice(self.arr)
        self.index, self.comps, self.mids = binary_search(self.arr, self.target)
        self.answer = self.index if self.task_type == "index" else self.comps

    def _descr(self, language):
        ru = language == "ru"
        arr = " ".join(map(str, self.arr))
        rule = (("Массив упорядочен по возрастанию, индексы с 0. "
                 "Середина отрезка [lo, hi] равна (lo + hi) // 2. "
                 "Каждое обращение к середине — одно сравнение.") if ru else
                ("The array is strictly increasing, indices start at 0. "
                 "The midpoint of [lo, hi] is (lo + hi) // 2. "
                 "Each look at the midpoint counts as one comparison."))
        if self.task_type == "index":
            ask = ((f"Массив: {arr}. Найдите индекс числа {self.target}.") if ru else
                   (f"Array: {arr}. Find the index of {self.target}."))
        else:
            ask = ((f"Массив: {arr}. Сколько сравнений сделает двоичный поиск числа {self.target}?")
                   if ru else
                   (f"Array: {arr}. How many comparisons does binary search make to find {self.target}?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = ", ".join(f"mid={m} (a={self.arr[m]})" for m in self.mids)
        self.solution_steps = [
            ((f"Середины: {shown}. Индекс {self.index}, сравнений {self.comps}.") if ru else
             (f"Midpoints: {shown}. Index {self.index}, comparisons {self.comps}.")),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
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
