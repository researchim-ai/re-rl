"""PancakeTraceTask — префиксные перевороты стопки.

Переворот k разворачивает первые k блинов. Число блинов и число переворотов растут с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _checksum(perm: List[int]) -> int:
    return sum(index * value for index, value in enumerate(perm, 1))


class PancakeTraceTask(BaseMathTask):
    TASK_TYPE = "pancake_trace"
    TASK_TYPES = ["place", "checksum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = list(range(1, self.n + 1))
        random.shuffle(self.start)
        self.flips = [random.randint(1, self.n) for _ in range(self.n)]
        self.perm = self.start[:]
        self.states: List[List[int]] = []
        for width in self.flips:
            self.perm[:width] = reversed(self.perm[:width])
            self.states.append(self.perm[:])
        self.place = self.perm.index(1) + 1
        self.checksum = _checksum(self.perm)
        self.answer = self.place if self.task_type == "place" else self.checksum
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        start = " ".join(str(item) for item in self.start)
        flips = ", ".join(str(item) for item in self.flips)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, n=self.n, start=start, flips=flips)

    def solve(self):
        steps = []
        for index, (width, state) in enumerate(zip(self.flips, self.states), 1):
            shown = " ".join(str(item) for item in state)
            steps.append(texts.t("s2", self.language, i=index, width=width, state=shown))
        steps.append(texts.t("s3", self.language, place=self.place, checksum=self.checksum))
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
