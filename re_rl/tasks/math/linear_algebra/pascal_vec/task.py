"""PascalVecTask — умножение вектора на матрицу Паскаля.

В строке k стоит биномиальный коэффициент, а обратная матрица возвращает вектор знаками минус единицы.
Длина вектора растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pascal_apply(values: Sequence[int]) -> List[Tuple[int, int]]:
    if not values:
        raise RuntimeError("pascal mismatch")
    images = []
    trace = []
    for row, _value in enumerate(values):
        comb = 1
        image = 0
        for col in range(row + 1):
            image += comb * values[col]
            comb = comb * (row - col) // (col + 1)
        images.append(image)
        comb = 1
        recovered = 0
        for col in range(row + 1):
            sign = 1 if (row - col) % 2 == 0 else -1
            recovered += sign * comb * images[col]
            comb = comb * (row - col) // (col + 1)
        if recovered != values[row]:
            raise RuntimeError("pascal mismatch")
        trace.append((image, recovered))
    return trace


class PascalVecTask(BaseMathTask):
    TASK_TYPE = "pascal_vec"
    TASK_TYPES = ["last", "total"]

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
        self.n = max(1, int(p["n"]))
        self.values = [random.randint(-3, 3) for _ in range(self.n)]
        self.trace = pascal_apply(self.values)
        self.last = self.trace[-1][0]
        self.total = sum(image for image, _back in self.trace)
        self.answer = self.last if self.task_type == "last" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(value) for value in self.values)

    def _descr(self, language):
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, image=image, back=back)
            for index, (image, back) in enumerate(self.trace)
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
