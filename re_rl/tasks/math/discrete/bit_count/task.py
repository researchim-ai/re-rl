"""BitCountTask — единицы и длина двоичной записи.

Для n ≥ 1 длина равна floor(log2 n) + 1, число единиц считается по записи.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BitCountTask(BaseMathTask):
    TASK_TYPE = "bit_count"
    TASK_TYPES = ["ones", "width"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 16}, 2: {"n": 32}, 3: {"n": 64}, 4: {"n": 100}, 5: {"n": 200},
        6: {"n": 500}, 7: {"n": 1000}, 8: {"n": 4000}, 9: {"n": 10000}, 10: {"n": 50000},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = random.randint(1, int(p["n"]))
        self.binary = bin(self.n)[2:]
        self.ones = self.binary.count("1")
        self.width = len(self.binary)
        self.answer = self.ones if self.task_type == "ones" else self.width
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "ones" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = texts.t("s2", self.language, n=self.n, binary=self.binary, ones=self.ones, width=self.width)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
