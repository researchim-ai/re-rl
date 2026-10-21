"""HeapTask — построение максимум-кучи.

Индексы с 0, дети вершины i — это 2*i+1 и 2*i+2. Вниз уходит больший ребёнок.
Подтипы:
- ``heapify`` — куча после просеивания всех внутренних вершин снизу вверх;
- ``sift``    — куча после одного просеивания корня (корень заранее испорчен).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def sift_down(values: List[int], start: int) -> None:
    i = start
    n = len(values)
    while True:
        left, right = 2 * i + 1, 2 * i + 2
        largest = i
        if left < n and values[left] > values[largest]:
            largest = left
        if right < n and values[right] > values[largest]:
            largest = right
        if largest == i:
            return
        values[i], values[largest] = values[largest], values[i]
        i = largest


def heapify(values: List[int]) -> List[int]:
    heap = list(values)
    for i in range(len(heap) // 2 - 1, -1, -1):
        sift_down(heap, i)
    return heap


class HeapTask(BaseMathTask):
    TASK_TYPE = "heap_array"
    TASK_TYPES = ["heapify", "sift"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "mag": 9}, 2: {"n": 5, "mag": 9}, 3: {"n": 5, "mag": 12},
        4: {"n": 6, "mag": 12}, 5: {"n": 7, "mag": 15}, 6: {"n": 7, "mag": 15},
        7: {"n": 8, "mag": 20}, 8: {"n": 9, "mag": 20}, 9: {"n": 10, "mag": 25},
        10: {"n": 12, "mag": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        raw = [random.randint(1, self.mag) for _ in range(self.n)]
        if self.task_type == "heapify":
            self.source = raw
            self.answer_list = heapify(raw)
        else:
            heap = heapify(raw)
            heap[0] = min(heap) - 1
            self.source = list(heap)
            sift_down(heap, 0)
            self.answer_list = heap
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _arr(self, values: List[int]) -> str:
        return " ".join(map(str, values))

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        data = self._arr(self.source)
        if self.task_type == "heapify":
            ask = ((texts.t('s1', language, data=data)))
        else:
            ask = ((texts.t('s2', language, data=data)))
        return f"{rule} {ask}"

    def solve(self):
        shown = ", ".join(map(str, self.answer_list))
        self.solution_steps = [
            ((texts.t('s3', self.language, shown=shown))),
            ((texts.common('answer_line', self.language, answer=shown))),
        ]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int_sequence(prediction, self.answer_list)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
