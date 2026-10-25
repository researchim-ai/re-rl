"""HammingSmoothTask — числа Хэмминга, гладкие по 2, 3 и 5.

Начните с 1. Следующее число — минимум из удвоенного, утроенного и упятерённого уже взятых, без повторов.
Номер числа растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hamming_trace(count: int) -> List[Tuple[int, int, int, int]]:
    values = [1]
    i2 = i3 = i5 = 0
    trace = [(1, 0, 0, 0)]
    while len(values) < count:
        nxt = min(values[i2] * 2, values[i3] * 3, values[i5] * 5)
        values.append(nxt)
        if nxt == values[i2] * 2:
            i2 += 1
        if nxt == values[i3] * 3:
            i3 += 1
        if nxt == values[i5] * 5:
            i5 += 1
        trace.append((nxt, i2, i3, i5))
    return trace


class HammingSmoothTask(BaseMathTask):
    TASK_TYPE = "hamming_smooth"
    TASK_TYPES = ["value", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 8},
        5: {"n": 10}, 6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16},
        9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = hamming_trace(self.n)
        self.value = self.trace[-1][0]
        self.total = sum(item[0] for item in self.trace)
        self.answer = self.value if self.task_type == "value" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, i2=i2, i3=i3, i5=i5)
            for index, (value, i2, i3, i5) in enumerate(self.trace, 1)
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
