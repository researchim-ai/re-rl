"""TriPermTask — перманент трёхдиагональной матрицы.

Следующий перманент равен диагонали на предыдущий плюс произведение уступа на перманент ещё раньше.
Порядок матрицы растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _ryser(diag: Sequence[int], upper: Sequence[int], lower: Sequence[int]) -> int:
    width = len(diag)
    total = 0
    for mask in range(1 << width):
        sign = 1 if (width - mask.bit_count()) % 2 == 0 else -1
        prod = 1
        for row in range(width):
            summed = 0
            for col in range(max(0, row - 1), min(width, row + 2)):
                if (mask >> col) & 1:
                    if col == row:
                        summed += diag[row]
                    elif col == row + 1:
                        summed += upper[row]
                    else:
                        summed += lower[col]
            prod *= summed
        total += sign * prod
    return total


def tri_perm(diag: Sequence[int], upper: Sequence[int], lower: Sequence[int]) -> List[Tuple[int, int]]:
    width = len(diag)
    if width < 1 or len(upper) != width - 1 or len(lower) != width - 1:
        raise RuntimeError("perm mismatch")
    older = 1
    previous = 1
    trace = []
    current = 1
    for index, item in enumerate(diag):
        if index == 0:
            current = item
        else:
            current = item * previous + upper[index - 1] * lower[index - 1] * older
        trace.append((current, previous))
        older, previous = previous, current
    if current != _ryser(diag, upper, lower):
        raise RuntimeError("perm mismatch")
    return trace


class TriPermTask(BaseMathTask):
    TASK_TYPE = "tri_perm"
    TASK_TYPES = ["perm", "prev"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.diag = [random.randint(1, 3) for _ in range(self.n)]
        self.upper = [random.randint(-1, 1) for _ in range(self.n - 1)]
        self.lower = [random.randint(-1, 1) for _ in range(self.n - 1)]
        self.trace = tri_perm(self.diag, self.upper, self.lower)
        self.perm = self.trace[-1][0]
        self.prev = self.trace[-1][1]
        self.answer = self.perm if self.task_type == "perm" else self.prev
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _nums(self, values: Sequence[int]) -> str:
        return " ".join(str(value) for value in values)

    def _descr(self, language):
        key = "s0" if self.task_type == "perm" else "s1"
        return texts.t(
            key, language, n=self.n, diag=self._nums(self.diag),
            upper=self._nums(self.upper), lower=self._nums(self.lower),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, perm=perm, prev=prev)
            for index, (perm, prev) in enumerate(self.trace, 1)
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
