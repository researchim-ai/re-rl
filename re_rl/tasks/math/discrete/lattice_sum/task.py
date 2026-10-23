"""LatticeSumTask — сумма целых частей i*a/b.

Порог задан заранее. Номер слагаемого, после которого сумма его достигает, тоже целый.
Число слагаемых растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lattice_trace(count: int, numer: int, denom: int, threshold: int) -> List[Tuple[int, int, int]]:
    total = 0
    cross = 0
    trace = []
    for index in range(1, count + 1):
        term = (index * numer) // denom
        total += term
        if cross == 0 and threshold > 0 and total >= threshold:
            cross = index
        trace.append((term, total, cross))
    return trace


class LatticeSumTask(BaseMathTask):
    TASK_TYPE = "lattice_sum"
    TASK_TYPES = ["total", "cross"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "b": 2}, 2: {"n": 4, "b": 3}, 3: {"n": 5, "b": 3},
        4: {"n": 6, "b": 4}, 5: {"n": 7, "b": 4}, 6: {"n": 8, "b": 5},
        7: {"n": 10, "b": 5}, 8: {"n": 12, "b": 6}, 9: {"n": 14, "b": 7},
        10: {"n": 16, "b": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.denom = max(1, int(p["b"]))
        self.numer = random.randint(1, self.denom)
        raw = sum((index * self.numer) // self.denom for index in range(1, self.n + 1))
        self.threshold = raw // 2 + 1 if raw else 0
        self.trace = lattice_trace(self.n, self.numer, self.denom, self.threshold)
        _, self.total, self.cross = self.trace[-1]
        self.answer = self.total if self.task_type == "total" else self.cross
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(
            key, language, n=self.n, numer=self.numer, denom=self.denom, threshold=self.threshold,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, term=term, total=total, cross=cross)
            for index, (term, total, cross) in enumerate(self.trace, 1)
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
