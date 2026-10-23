"""BilliardBoxTask — шар в прямоугольнике под углом 45°.

Старт из угла (0, 0), компоненты скорости равны по модулю.
Удар о сторону меняет знак одной компоненты. Попадание в угол останавливает полёт.
Число ударов о стороны растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Hit = Tuple[int, int, int]


def billiard_trace(width: int, height: int) -> Tuple[List[Hit], Tuple[int, int]]:
    x = y = 0
    dx = dy = 1
    trace: List[Hit] = []
    for _ in range(width + height + 5):
        to_vertical = (width - x) if dx == 1 else x
        to_horizontal = (height - y) if dy == 1 else y
        if to_vertical == to_horizontal:
            corner = (x + dx * to_vertical, y + dy * to_horizontal)
            return trace, corner
        if to_vertical < to_horizontal:
            x += dx * to_vertical
            y += dy * to_vertical
            dx = -dx
            trace.append((1, x, y))
        else:
            x += dx * to_horizontal
            y += dy * to_horizontal
            dy = -dy
            trace.append((2, x, y))
    raise RuntimeError("billiard")


def choose_table(hits: int) -> Tuple[int, int]:
    found = []
    mixed = []
    limit = hits + 3
    for width in range(1, limit + 1):
        for height in range(1, limit + 1):
            if width == height:
                continue
            trace, _corner = billiard_trace(width, height)
            if len(trace) != hits:
                continue
            found.append((width, height))
            if {item[0] for item in trace} == {1, 2}:
                mixed.append((width, height))
    pool = mixed or found
    return random.choice(pool)


class BilliardBoxTask(BaseMathTask):
    TASK_TYPE = "billiard_box"
    TASK_TYPES = ["hits", "height"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.width, self.height = choose_table(self.n)
        self.trace, self.corner = billiard_trace(self.width, self.height)
        self.k = random.randint(1, self.n)
        self.hit_count = len(self.trace)
        self.mark = self.trace[self.k - 1][2]
        self.answer = self.hit_count if self.task_type == "hits" else self.mark
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "hits" else "s1"
        return texts.t(key, language, width=self.width, height=self.height, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, side=side, x=x, y=y)
            for index, (side, x, y) in enumerate(self.trace, 1)
        ]
        steps.append(texts.t(
            "s3", self.language, hits=self.hit_count, x=self.corner[0], y=self.corner[1],
        ))
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
