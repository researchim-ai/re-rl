"""FloatLoadTask — плавание и затопление в сосуде с пределом уровня.

Плотность воды равна 1. Плавающий предмет вытесняет свой вес, тонущий — свой объём.
Уровень не поднимается выше предела. Число предметов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Object = Tuple[int, int]


def load_trace(limit: int, objects: Sequence[Object]) -> List[Tuple[int, int]]:
    level = 0
    full = 0
    trace = []
    for index, (weight, volume) in enumerate(objects, 1):
        want = weight if weight <= volume else volume
        room = limit - level
        if room < 0:
            room = 0
        level += want if want < room else room
        if full == 0 and level == limit:
            full = index
        trace.append((level, full))
    return trace


class FloatLoadTask(BaseMathTask):
    TASK_TYPE = "float_load"
    TASK_TYPES = ["level", "full"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.objects = [
            (random.randint(1, 6), random.randint(1, 6))
            for _ in range(self.n)
        ]
        total = sum(weight if weight <= volume else volume for weight, volume in self.objects)
        if random.randint(0, 1) == 0:
            self.limit = total + random.randint(1, 3)
        else:
            self.limit = random.randint(1, total)
        self.trace = load_trace(self.limit, self.objects)
        self.level, self.full = self.trace[-1]
        self.answer = self.level if self.task_type == "level" else self.full
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{weight}-{volume}" for weight, volume in self.objects)
        key = "s0" if self.task_type == "level" else "s1"
        return texts.t(key, language, limit=self.limit, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, weight=weight, volume=volume, level=level, full=full)
            for index, ((weight, volume), (level, full)) in enumerate(zip(self.objects, self.trace), 1)
        ]
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
