"""CrackCloseTask — щель сначала зарастает, потом узкие перемычки снимаются.

Сначала ноль становится единицей, если в окне есть единица. Потом единица остаётся, только если окно сплошное.
Обе операции считает SciPy. Длина ряда растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

import numpy as np
from scipy.ndimage import binary_dilation, binary_erosion

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_SHAPE = np.ones(3, dtype=bool)


def crack_trace(bits: Sequence[int]) -> List[Tuple[int, int, int]]:
    row = np.asarray(bits, dtype=bool)
    wide = binary_dilation(row, structure=_SHAPE).astype(int)
    shut = binary_erosion(wide.astype(bool), structure=_SHAPE).astype(int)
    filled = 0
    trace = []
    for old, grown, closed in zip(row.astype(int), wide, shut):
        if old == 0 and int(closed) == 1:
            filled += 1
        trace.append((int(grown), int(closed), filled))
    return trace


class CrackCloseTask(BaseMathTask):
    TASK_TYPE = "crack_close"
    TASK_TYPES = ["filled", "open"]

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
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = crack_trace(self.bits)
        self.filled = self.trace[-1][2]
        self.open = self.n - sum(item[1] for item in self.trace)
        self.answer = self.filled if self.task_type == "filled" else self.open
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(bit) for bit in self.bits)
        key = "s0" if self.task_type == "filled" else "s1"
        return texts.t(key, language, n=self.n, bits=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, wide=wide, shut=shut, filled=filled)
            for index, (wide, shut, filled) in enumerate(self.trace, 1)
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
