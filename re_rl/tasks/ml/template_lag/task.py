"""TemplateLagTask — лучшее наложение короткого шаблона на ряд.

Счёт положения — сумма произведений шаблона и куска ряда. Корреляцию считает SciPy.
При равенстве остаётся более раннее положение. Число положений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
from scipy.signal import correlate

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def match_trace(signal: Sequence[int], pattern: Sequence[int]) -> List[Tuple[int, int, int]]:
    scores = correlate(np.asarray(signal), np.asarray(pattern), mode="valid")
    best = None
    best_at = 1
    trace = []
    for index, score in enumerate(scores, 1):
        number = int(score)
        if best is None or number > best:
            best = number
            best_at = index
        trace.append((number, best, best_at))
    return trace


class TemplateLagTask(BaseMathTask):
    TASK_TYPE = "template_lag"
    TASK_TYPES = ["lag", "score"]

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
        self.pattern = [random.randint(-2, 3) for _ in range(2)]
        self.signal = [random.randint(0, 5) for _ in range(self.n + 1)]
        self.trace = match_trace(self.signal, self.pattern)
        self.lag = self.trace[-1][2]
        self.score = self.trace[-1][1]
        self.answer = self.lag if self.task_type == "lag" else self.score
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        signal = ", ".join(str(value) for value in self.signal)
        pattern = ", ".join(str(value) for value in self.pattern)
        key = "s0" if self.task_type == "lag" else "s1"
        return texts.t(key, language, n=self.n, signal=signal, pattern=pattern)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, score=score, best=best, lag=lag)
            for index, (score, best, lag) in enumerate(self.trace, 1)
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
