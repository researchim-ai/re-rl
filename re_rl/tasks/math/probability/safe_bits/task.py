"""SafeBitsTask — число двоичных строк без двух единиц подряд.

Строка может кончаться нулём после любой подходящей или единицей только после нуля.
Длина строки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def norepeat_trace(length: int) -> List[Tuple[int, int]]:
    end0 = 1
    end1 = 1
    trace = [(end0 + end1, end1)]
    for _ in range(1, length):
        end0, end1 = end0 + end1, end0
        trace.append((end0 + end1, end1))
    return trace


class SafeBitsTask(BaseMathTask):
    TASK_TYPE = "safe_bits"
    TASK_TYPES = ["count", "tail"]

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
        self.trace = norepeat_trace(self.n)
        self.count = self.trace[-1][0]
        self.tail = self.trace[-1][1]
        self.answer = self.count if self.task_type == "count" else self.tail
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, count=count, tail=tail)
            for index, (count, tail) in enumerate(self.trace, 1)
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
