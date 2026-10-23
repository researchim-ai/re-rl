"""RetryGoalTask — повторы по круговому шаблону успеха.

Шаблон из нулей и единиц повторяется. Единица — удачная попытка.
Нужно набрать заданное число успехов. Попыток не больше утроенного числа успехов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def retry_until(pattern: Sequence[int], successes: int) -> List[Tuple[int, int, int]]:
    got = 0
    fails = 0
    tries = 0
    trace = []
    while got < successes:
        bit = pattern[tries % len(pattern)]
        tries += 1
        if bit:
            got += 1
        else:
            fails += 1
        trace.append((tries, got, fails))
    return trace


class RetryGoalTask(BaseMathTask):
    TASK_TYPE = "retry_goal"
    TASK_TYPES = ["tries", "fails"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.pattern = [random.randint(0, 1) for _ in range(3)]
        if 1 not in self.pattern:
            self.pattern[0] = 1
        self.trace = retry_until(self.pattern, self.n)
        self.tries, _, self.fails = self.trace[-1]
        self.answer = self.tries if self.task_type == "tries" else self.fails
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(bit) for bit in self.pattern)
        key = "s0" if self.task_type == "tries" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=tries, got=got, fails=fails)
            for tries, got, fails in self.trace
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
