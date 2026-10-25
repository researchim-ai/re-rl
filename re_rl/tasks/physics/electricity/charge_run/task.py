"""ChargeRunTask — накопление заряда как дискретный интегратор.

Каждый отсчёт прибавляется к уже собранному заряду. Накопление считает SciPy.
Длина ряда растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

import numpy as np
from scipy.signal import lfilter

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def coulomb_trace(samples: Sequence[int]) -> List[int]:
    filtered = lfilter([1.0], [1.0, -1.0], np.asarray(samples, dtype=float))
    total = 0
    trace = []
    for sample, accumulated in zip(samples, filtered):
        total += sample
        if int(round(float(accumulated))) != total:
            raise RuntimeError("accumulator mismatch")
        trace.append(total)
    return trace


class ChargeRunTask(BaseMathTask):
    TASK_TYPE = "charge_run"
    TASK_TYPES = ["total", "hit"]

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
        self.samples = [random.randint(0, 6) for _ in range(self.n)]
        self.trace = coulomb_trace(self.samples)
        self.total = self.trace[-1]
        half = self.total // 2
        self.hit = 1
        for index, value in enumerate(self.trace, 1):
            if value >= half:
                self.hit = index
                break
        self.answer = self.total if self.task_type == "total" else self.hit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(sample) for sample in self.samples)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, samples=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, sample=sample, total=total)
            for index, (sample, total) in enumerate(zip(self.samples, self.trace), 1)
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
