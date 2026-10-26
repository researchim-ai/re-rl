"""PermOrderTask — порядок подстановки как наименьшее общее кратное циклов.

Порядок проверяется повторным применением: эта степень впервые тождественна.
Длина подстановки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _lcm(left: int, right: int) -> int:
    if left == 0 or right == 0:
        return 0
    return left // math.gcd(left, right) * right


def _apply(images: Sequence[int], times: int) -> List[int]:
    current = list(range(1, len(images) + 1))
    for _ in range(times):
        current = [images[item - 1] for item in current]
    return current


def perm_lcm(images: Sequence[int]) -> List[Tuple[int, int, int]]:
    size = len(images)
    seen = [0] * (size + 1)
    order = 1
    moved = 0
    trace = []
    for start in range(1, size + 1):
        if seen[start]:
            trace.append((0, order, moved))
            continue
        length = 0
        point = start
        while not seen[point]:
            seen[point] = 1
            point = images[point - 1]
            length += 1
        if length > 1:
            moved += 1
        order = _lcm(order, length)
        trace.append((length, order, moved))
    identity = list(range(1, size + 1))
    if _apply(images, order) != identity:
        raise RuntimeError("order mismatch")
    divisor = 1
    while divisor * divisor <= order:
        if order % divisor == 0:
            for piece in (divisor, order // divisor):
                if piece < order and _apply(images, piece) == identity:
                    raise RuntimeError("order mismatch")
        divisor += 1
    return trace


class PermOrderTask(BaseMathTask):
    TASK_TYPE = "perm_order"
    TASK_TYPES = ["order", "moved"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.images = list(range(1, self.n + 1))
        random.shuffle(self.images)
        self.trace = perm_lcm(self.images)
        self.order = self.trace[-1][1]
        self.moved = self.trace[-1][2]
        self.answer = self.order if self.task_type == "order" else self.moved
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(image) for image in self.images)

    def _descr(self, language):
        key = "s0" if self.task_type == "order" else "s1"
        return texts.t(key, language, n=self.n, images=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, length=length, order=order, moved=moved)
            for index, (length, order, moved) in enumerate(self.trace, 1)
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
