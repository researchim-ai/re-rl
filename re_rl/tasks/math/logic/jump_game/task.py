"""JumpGameTask — минимум прыжков до последнего индекса.

a[i] — насколько далеко можно прыгнуть из i. Массив строится достижимым:
каждый элемент, кроме последнего, не меньше 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


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
        raise RuntimeError(texts.literal('literals.s2'))
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
        data = " ".join(map(str, self.jumps))
        return ((texts.t('s0', language, data=data)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
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
