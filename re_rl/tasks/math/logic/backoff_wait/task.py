"""BackoffWaitTask — попытка проходит, только если её время не раньше готовности.

Успех сдвигает готовность на текущее ожидание, а ожидание удваивается.
Неудача ожидание не меняет. Число попыток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def backoff_trace(times: Sequence[int]) -> List[Tuple[int, int, int, int]]:
    ready = 0
    wait = 1
    ok = 0
    trace = []
    for moment in times:
        if moment >= ready:
            ok += 1
            ready = moment + wait
            wait *= 2
            flag = 1
        else:
            flag = 0
        trace.append((flag, ok, ready, wait))
    return trace


class BackoffWaitTask(BaseMathTask):
    TASK_TYPE = "backoff_wait"
    TASK_TYPES = ["successes", "wait"]

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
        moment = 0
        self.times = []
        for _ in range(self.n):
            moment += random.randint(0, 3)
            self.times.append(moment)
        self.trace = backoff_trace(self.times)
        _, self.successes, _, self.wait = self.trace[-1]
        self.answer = self.successes if self.task_type == "successes" else self.wait
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(moment) for moment in self.times)
        key = "s0" if self.task_type == "successes" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, moment=moment, flag=flag,
                ok=ok, ready=ready, wait=wait,
            )
            for index, (moment, (flag, ok, ready, wait)) in enumerate(zip(self.times, self.trace), 1)
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
