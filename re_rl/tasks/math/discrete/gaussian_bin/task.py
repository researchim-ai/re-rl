"""GaussianBinTask — гауссов биномиальный коэффициент.

Строка 0 равна 1. Клетка k строки m равна клетке k предыдущей строки плюс q в степени m-k, умноженное на клетку k-1. Отсутствующая клетка равна 0.
Порядок и основание растут с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def gauss_product(order: int, choose: int, base: int) -> int:
    if choose < 0 or choose > order:
        return 0
    choose = min(choose, order - choose)
    numer = 1
    denom = 1
    for index in range(1, choose + 1):
        numer *= base ** (order - choose + index) - 1
        denom *= base ** index - 1
    assert numer % denom == 0
    return numer // denom


def gauss_rows(order: int, base: int) -> List[List[int]]:
    row = [1]
    rows = [row]
    for width in range(1, order + 1):
        nxt = []
        for choose in range(width + 1):
            left = row[choose] if choose < len(row) else 0
            down = row[choose - 1] if choose else 0
            nxt.append(left + (base ** (width - choose)) * down)
        row = nxt
        rows.append(row)
    for width, values in enumerate(rows):
        for choose, value in enumerate(values):
            assert value == gauss_product(width, choose, base)
    return rows


class GaussianBinTask(BaseMathTask):
    TASK_TYPE = "gaussian_bin"
    TASK_TYPES = ["entry", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "q": 2}, 2: {"n": 3, "q": 2}, 3: {"n": 4, "q": 2},
        4: {"n": 5, "q": 2}, 5: {"n": 6, "q": 2}, 6: {"n": 7, "q": 3},
        7: {"n": 8, "q": 3}, 8: {"n": 9, "q": 3}, 9: {"n": 10, "q": 3},
        10: {"n": 12, "q": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.base = max(2, int(p["q"]))
        self.rows = gauss_rows(self.n, self.base)
        self.k = random.randint(0, self.n)
        self.entry = self.rows[-1][self.k]
        self.total = sum(self.rows[-1])
        self.answer = self.entry if self.task_type == "entry" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, q=self.base, k=self.k)

    def solve(self):
        steps = [texts.t("s3", self.language)]
        for width, row in enumerate(self.rows[1:], 1):
            previous = self.rows[width - 1]
            for choose, value in enumerate(row):
                left = previous[choose] if choose < len(previous) else 0
                down = previous[choose - 1] if choose and previous else 0
                power = self.base ** (width - choose) if width else 1
                steps.append(texts.t(
                    "s2", self.language, m=width, k=choose, left=left,
                    power=power, down=down, value=value,
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
