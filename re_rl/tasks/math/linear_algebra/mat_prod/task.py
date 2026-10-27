"""MatProdTask — произведение цепочки матриц 2 на 2.

Накопитель умножается справа на следующую матрицу, а определитель перемножается.
Число матриц растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Mat = Tuple[int, int, int, int]
State = Tuple[int, int, int, int, int]


def prod_fold(mats: Sequence[Mat]) -> List[State]:
    if not mats:
        raise RuntimeError("prod mismatch")
    a, b, c, d = mats[0]
    det = a * d - b * c
    acc = (a, b, c, d)
    trace = [(a, b, c, d, det)]
    for a, b, c, d in mats[1:]:
        p00, p01, p10, p11 = acc
        acc = (
            p00 * a + p01 * c,
            p00 * b + p01 * d,
            p10 * a + p11 * c,
            p10 * b + p11 * d,
        )
        det *= a * d - b * c
        if det != acc[0] * acc[3] - acc[1] * acc[2]:
            raise RuntimeError("prod mismatch")
        trace.append((acc[0], acc[1], acc[2], acc[3], det))
    return trace


class MatProdTask(BaseMathTask):
    TASK_TYPE = "mat_prod"
    TASK_TYPES = ["entry", "det"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.mats = [
            (
                random.randint(-1, 1), random.randint(-1, 1),
                random.randint(-1, 1), random.randint(-1, 1),
            )
            for _ in range(self.n)
        ]
        self.trace = prod_fold(self.mats)
        self.entry = self.trace[-1][0]
        self.det = self.trace[-1][4]
        self.answer = self.entry if self.task_type == "entry" else self.det
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{a} {b} {c} {d}" for a, b, c, d in self.mats)

    def _descr(self, language):
        key = "s0" if self.task_type == "entry" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, k=index, p00=p00, p01=p01, p10=p10, p11=p11, det=det)
            for index, (p00, p01, p10, p11, det) in enumerate(self.trace, 1)
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
