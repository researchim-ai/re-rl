"""PathGreenTask — потенциал единичного источника на отрезке с нулевыми концами.

В узле i левее источника или в нём потенциал равен i, умноженному на длину без номера источника.
Правее он равен номеру источника, умноженному на длину без i. Лапласиан равен нулю везде, кроме источника.
Число внутренних узлов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def green_trace(length: int, spot: int) -> List[Tuple[int, int]]:
    if length < 2 or not 0 < spot < length:
        raise RuntimeError("green mismatch")
    values = [0] * (length + 1)
    total = 0
    trace = []
    for index in range(1, length):
        if index <= spot:
            value = index * (length - spot)
        else:
            value = spot * (length - index)
        values[index] = value
        total += value
        trace.append((value, total))
    for index in range(1, length):
        lap = values[index - 1] - 2 * values[index] + values[index + 1]
        expect = -length if index == spot else 0
        if lap != expect:
            raise RuntimeError("green mismatch")
    return trace


class PathGreenTask(BaseMathTask):
    TASK_TYPE = "path_green"
    TASK_TYPES = ["peak", "total"]

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
        self.length = self.n + 1
        self.spot = random.randint(1, self.n)
        self.trace = green_trace(self.length, self.spot)
        self.peak = self.trace[self.spot - 1][0]
        self.total = self.trace[-1][1]
        self.answer = self.peak if self.task_type == "peak" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "peak" else "s1"
        return texts.t(key, language, n=self.n, length=self.length, spot=self.spot)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, total=total)
            for index, (value, total) in enumerate(self.trace, 1)
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
