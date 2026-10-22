"""HornerEvalTask — значение многочлена схемой Горнера.

Число коэффициентов растёт с уровнем. Каждый шаг зависит от предыдущего накопленного значения.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HornerEvalTask(BaseMathTask):
    TASK_TYPE = "horner_eval"
    TASK_TYPES = ["value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "x": 2, "c": 4}, 2: {"n": 2, "x": 3, "c": 5},
        3: {"n": 3, "x": 3, "c": 5}, 4: {"n": 3, "x": 3, "c": 6},
        5: {"n": 4, "x": 3, "c": 4}, 6: {"n": 5, "x": 2, "c": 5},
        7: {"n": 6, "x": 2, "c": 4}, 8: {"n": 6, "x": 3, "c": 3},
        9: {"n": 7, "x": 2, "c": 4}, 10: {"n": 8, "x": 2, "c": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "value"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        span = int(p["c"])
        self.x = random.randint(1, int(p["x"]))
        self.coeffs: List[int] = [random.randint(-span, span) for _ in range(self.n)]
        self.trace: List[int] = []
        acc = 0
        for coeff in self.coeffs:
            acc = acc * self.x + coeff
            self.trace.append(acc)
        self.answer = acc
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.coeffs)
        return texts.t("s0", language, n=self.n, listing=listing, x=self.x)

    def solve(self):
        steps = []
        previous = 0
        for index, (coeff, acc) in enumerate(zip(self.coeffs, self.trace), 1):
            steps.append(texts.t(
                "s1", self.language, i=index, prev=previous, x=self.x, coeff=coeff, acc=acc,
            ))
            previous = acc
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
