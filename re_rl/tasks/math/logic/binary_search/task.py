"""BinarySearchTask — двоичный поиск в отсортированном массиве.

Границы включительные, середина mid = (lo + hi) // 2. Цель всегда есть в массиве.
Сравнение — одно обращение к элементу середины, включая удачное.

Подтипы: ``index`` (с нуля) и ``comparisons``.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
    raise RuntimeError(texts.literal('literals.s4'))


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
        arr = " ".join(map(str, self.arr))
        rule = texts.t("literals.s0", language)
        if self.task_type == "index":
            ask = ((texts.t('s1', language, arr=arr, target=self.target)))
        else:
            ask = ((texts.t('s2', language, arr=arr, target=self.target)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        shown = ", ".join(f"mid={m} (a={self.arr[m]})" for m in self.mids)
        self.solution_steps = [
            ((texts.t('s3', self.language, shown=shown, index=self.index, comps=self.comps))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
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
