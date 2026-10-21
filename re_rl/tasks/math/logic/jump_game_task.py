"""JumpGameTask — минимум прыжков до последнего индекса.

a[i] — насколько далеко можно прыгнуть из i. Массив строится достижимым:
каждый элемент, кроме последнего, не меньше 1.
"""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def min_jumps(jumps: List[int]) -> int:
    n = len(jumps)
    if n <= 1:
        return 0
    count = 0
    end = 0
    farthest = 0
    for i in range(n - 1):
        farthest = max(farthest, i + jumps[i])
        if i == end:
            count += 1
            end = farthest
            if end >= n - 1:
                break
    if end < n - 1:
        raise RuntimeError("последняя клетка недостижима")
    return count


class JumpGameTask(BaseMathTask):
    TASK_TYPE = "jump_game"
    TASK_TYPES = ["min_jumps"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "reach": 2}, 2: {"n": 5, "reach": 2}, 3: {"n": 5, "reach": 3},
        4: {"n": 6, "reach": 3}, 5: {"n": 7, "reach": 3}, 6: {"n": 8, "reach": 3},
        7: {"n": 9, "reach": 4}, 8: {"n": 10, "reach": 4}, 9: {"n": 12, "reach": 4},
        10: {"n": 14, "reach": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.reach = int(p["reach"])
        self.task_type = "min_jumps"
        self.augment = augment
        self.jumps = [random.randint(1, self.reach) for _ in range(self.n - 1)] + [0]
        self.answer = min_jumps(self.jumps)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        data = " ".join(map(str, self.jumps))
        return ((f"Массив прыжков, индексы с 0: {data}. Из i можно перейти в любой индекс "
                 f"от i+1 до i+a[i] включительно. Найдите минимальное число прыжков до последнего индекса.")
                if ru else
                (f"Jump array, indices start at 0: {data}. From i you may move to any index "
                 f"from i+1 through i+a[i]. Find the minimum number of jumps to the last index."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ((f"Жадное расширение текущего окна даёт {self.answer} прыжков.") if ru else
             (f"Greedy expansion of the current window takes {self.answer} jumps.")),
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
