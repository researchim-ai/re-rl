"""CovPairTask — числитель ковариации пары наблюдений.

После каждой пары числитель равен N на сумму произведений минус произведение сумм.
Разность числителей дисперсий суммы и слагаемых равна его удвоению.
Число пар растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def cov_trace(pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    count = 0
    sx = sy = sxy = sx2 = sy2 = ssum = 0
    trace = []
    for left, right in pairs:
        count += 1
        sx += left
        sy += right
        sxy += left * right
        sx2 += left * left
        sy2 += right * right
        ssum += (left + right) * (left + right)
        cov = count * sxy - sx * sy
        var_x = count * sx2 - sx * sx
        var_y = count * sy2 - sy * sy
        var_sum = count * ssum - (sx + sy) * (sx + sy)
        cross = var_sum - var_x - var_y
        if cross != 2 * cov:
            raise RuntimeError("cov mismatch")
        trace.append((cov, cross))
    return trace


class CovPairTask(BaseMathTask):
    TASK_TYPE = "cov_pair"
    TASK_TYPES = ["cov", "cross"]

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
        self.pairs = [
            (random.randint(-3, 4), random.randint(-3, 4)) for _ in range(self.n)
        ]
        self.trace = cov_trace(self.pairs)
        self.cov = self.trace[-1][0]
        self.cross = self.trace[-1][1]
        self.answer = self.cov if self.task_type == "cov" else self.cross
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{left} {right}" for left, right in self.pairs)

    def _descr(self, language):
        key = "s0" if self.task_type == "cov" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cov=cov, cross=cross)
            for index, (cov, cross) in enumerate(self.trace, 1)
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
