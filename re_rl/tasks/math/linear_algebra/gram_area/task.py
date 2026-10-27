"""GramAreaTask — квадрат площади двух векторов.

Он равен произведению сумм квадратов минус квадрат скалярного произведения и сумме квадратов миноров.
Длина векторов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def gram_trace(left: Sequence[int], right: Sequence[int]) -> List[Tuple[int, int]]:
    if len(left) != len(right) or not left:
        raise RuntimeError("gram mismatch")
    dot = 0
    left_sq = 0
    right_sq = 0
    trace = []
    for u, v in zip(left, right):
        dot += u * v
        left_sq += u * u
        right_sq += v * v
        area = left_sq * right_sq - dot * dot
        if area < 0:
            raise RuntimeError("gram mismatch")
        trace.append((dot, area))
    minor = 0
    for i, u in enumerate(left):
        for j in range(i + 1, len(left)):
            cross = u * right[j] - left[j] * right[i]
            minor += cross * cross
    if minor != trace[-1][1]:
        raise RuntimeError("gram mismatch")
    return trace


class GramAreaTask(BaseMathTask):
    TASK_TYPE = "gram_area"
    TASK_TYPES = ["area", "dot"]

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
        self.left = [random.randint(-3, 3) for _ in range(self.n)]
        self.right = [random.randint(-3, 3) for _ in range(self.n)]
        self.trace = gram_trace(self.left, self.right)
        self.dot = self.trace[-1][0]
        self.area = self.trace[-1][1]
        self.answer = self.area if self.task_type == "area" else self.dot
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pair(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "area" else "s1"
        return texts.t(key, language, n=self.n, left=self._pair(self.left), right=self._pair(self.right))

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, dot=dot, area=area)
            for index, (dot, area) in enumerate(self.trace, 1)
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
