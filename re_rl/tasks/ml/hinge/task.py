"""HingeLossTask — кусочно-линейная потеря линейного классификатора.

Для примера (x, y), y = +1 или -1, потеря max(0, 1 - y*(w·x + b)).
Сумма по выборке целая, если веса и координаты целые.

Подтипы: суммарная потеря и число ошибок (потеря строго больше нуля).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Example = Tuple[int, int, int]


def hinge_one(w1: int, w2: int, b: int, ex: Example) -> int:
    x1, x2, y = ex
    margin = y * (w1 * x1 + w2 * x2 + b)
    return max(0, 1 - margin)


class HingeLossTask(BaseMathTask):
    TASK_TYPE = "hinge_loss"
    TASK_TYPES = ["total", "errors"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 2, "c": 2}, 2: {"m": 2, "c": 2}, 3: {"m": 3, "c": 2},
        4: {"m": 3, "c": 3}, 5: {"m": 4, "c": 3}, 6: {"m": 4, "c": 3},
        7: {"m": 5, "c": 3}, 8: {"m": 5, "c": 4}, 9: {"m": 6, "c": 4},
        10: {"m": 7, "c": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.m = int(p["m"])
        self.c = int(p["c"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.w1 = random.randint(-self.c, self.c)
        self.w2 = random.randint(-self.c, self.c)
        self.b = random.randint(-self.c, self.c)
        self.examples: List[Example] = [
            (random.randint(-self.c, self.c), random.randint(-self.c, self.c), random.choice([-1, 1]))
            for _ in range(self.m)
        ]
        self.losses = [hinge_one(self.w1, self.w2, self.b, ex) for ex in self.examples]
        self.total = sum(self.losses)
        self.errors = sum(1 for loss in self.losses if loss > 0)
        self.answer = self.total if self.task_type == "total" else self.errors
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        data = ", ".join(f"({x1}, {x2}, y={y})" for x1, x2, y in self.examples)
        rule = ((texts.t('s0', language)))
        weights = ((texts.t('s1', language, w1=self.w1, w2=self.w2, b=self.b, data=data)))
        ask = ((texts.t('s2', language) if self.task_type == "total" else
                texts.t('s3', language)))
        return f"{rule} {weights} {ask}"

    def solve(self):
        shown = ", ".join(str(v) for v in self.losses)
        step = ((texts.t('s4', self.language, shown=shown, total=self.total, errors=self.errors)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
