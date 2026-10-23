"""RateLimitTask — квота обслуживаний в скользящем окне времени.

Запрос проходит, если в окне уже обслужено меньше квоты. Время запросов растёт.
Число запросов растёт с уровнем, окно короткое.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rate_flags(times: Sequence[int], window: int, quota: int) -> List[int]:
    served = []
    flags = []
    for moment in times:
        served = [item for item in served if item >= moment - window + 1]
        if len(served) < quota:
            served.append(moment)
            flags.append(1)
        else:
            flags.append(0)
    return flags


class RateLimitTask(BaseMathTask):
    TASK_TYPE = "rate_limit"
    TASK_TYPES = ["served", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "w": 2, "q": 1}, 2: {"n": 3, "w": 2, "q": 1},
        3: {"n": 4, "w": 3, "q": 1}, 4: {"n": 5, "w": 3, "q": 2},
        5: {"n": 6, "w": 4, "q": 2}, 6: {"n": 7, "w": 4, "q": 2},
        7: {"n": 8, "w": 4, "q": 2}, 8: {"n": 10, "w": 5, "q": 2},
        9: {"n": 12, "w": 5, "q": 3}, 10: {"n": 14, "w": 5, "q": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.window = max(1, int(p["w"]))
        self.quota = max(1, int(p["q"]))
        moment = 0
        self.times = []
        for _ in range(self.n):
            moment += random.randint(1, 3)
            self.times.append(moment)
        self.flags = rate_flags(self.times, self.window, self.quota)
        self.served = sum(self.flags)
        self.k = random.randint(1, self.n)
        self.at_k = self.flags[self.k - 1]
        self.answer = self.served if self.task_type == "served" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(moment) for moment in self.times)
        key = "s0" if self.task_type == "served" else "s1"
        return texts.t(
            key, language, n=self.n, listing=listing, window=self.window,
            quota=self.quota, k=self.k,
        )

    def solve(self):
        running = 0
        steps = []
        for index, (moment, flag) in enumerate(zip(self.times, self.flags), 1):
            running += flag
            steps.append(texts.t(
                "s2", self.language, i=index, time=moment, flag=flag, served=running,
            ))
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
