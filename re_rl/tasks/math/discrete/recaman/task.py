"""RecamanTask — последовательность Рекамана.

На шаге t из текущего числа вычитается t, если результат положителен и ещё не встречался.
Иначе t прибавляется. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def recaman_trace(count: int) -> List[Tuple[int, int]]:
    seen = {0}
    value = 0
    subs = 0
    trace = []
    for step in range(1, count + 1):
        nxt = value - step
        if nxt > 0 and nxt not in seen:
            value = nxt
            subs += 1
        else:
            value = value + step
        seen.add(value)
        trace.append((value, subs))
    return trace


class RecamanTask(BaseMathTask):
    TASK_TYPE = "recaman"
    TASK_TYPES = ["last", "subs"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 18},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = recaman_trace(self.n)
        self.last, self.subs = self.trace[-1]
        self.answer = self.last if self.task_type == "last" else self.subs
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, subs=subs)
            for index, (value, subs) in enumerate(self.trace, 1)
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
