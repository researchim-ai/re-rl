"""ModChainTask — цепочка x → (a·x + b) mod m.

Число шагов растёт с уровнем, остаток на каждом шаге точный.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class ModChainTask(BaseMathTask):
    TASK_TYPE = "mod_chain"
    TASK_TYPES = ["final"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 5}, 2: {"n": 2, "m": 7}, 3: {"n": 3, "m": 8},
        4: {"n": 3, "m": 9}, 5: {"n": 4, "m": 10}, 6: {"n": 5, "m": 11},
        7: {"n": 6, "m": 12}, 8: {"n": 8, "m": 13}, 9: {"n": 9, "m": 15},
        10: {"n": 12, "m": 17},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "final"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.mod = max(2, int(p["m"]))
        self.start = random.randint(0, self.mod - 1)
        self.value = self.start
        self.ops: List[Tuple[int, int, int]] = []
        for _ in range(self.n):
            factor = random.randint(0, self.mod - 1)
            shift = random.randint(0, self.mod - 1)
            self.value = (self.value * factor + shift) % self.mod
            self.ops.append((factor, shift, self.value))
        self.answer = self.value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [
            texts.t("s1", language, i=i, factor=factor, shift=shift)
            for i, (factor, shift, _) in enumerate(self.ops, 1)
        ]
        return texts.t("s0", language, start=self.start, mod=self.mod, n=self.n, ops=" ".join(parts))

    def solve(self):
        steps = []
        previous = self.start
        for index, (factor, shift, value) in enumerate(self.ops, 1):
            steps.append(texts.t(
                "s2", self.language, i=index, prev=previous, factor=factor,
                shift=shift, mod=self.mod, value=value,
            ))
            previous = value
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
