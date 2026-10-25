"""InversionRowTask — инверсии перестановки.

Для каждого места считается, сколько меньших чисел стоит правее. Сумма — число инверсий.
Длина растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def inversion_trace(values: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for index, value in enumerate(values):
        here = sum(1 for other in values[index + 1:] if other < value)
        total += here
        trace.append((here, total))
    return trace


class InversionRowTask(BaseMathTask):
    TASK_TYPE = "inversion_row"
    TASK_TYPES = ["total", "here"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.values = list(range(1, self.n + 1))
        random.shuffle(self.values)
        self.trace = inversion_trace(self.values)
        self.total = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.trace[self.k - 1][0]
        self.answer = self.total if self.task_type == "total" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        values = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, values=values, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, here=here, total=total)
            for index, (value, (here, total)) in enumerate(zip(self.values, self.trace), 1)
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
