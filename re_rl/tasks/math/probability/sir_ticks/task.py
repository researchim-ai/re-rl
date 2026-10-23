"""SirTicksTask — дискретная эпидемия.

За тик заражается min(здоровые, заразные). Затем половина прежних заразных выздоравливает.
Новые заразные в этот тик не выздоравливают. Число тиков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def sir_tick(healthy: int, sick: int, recovered: int) -> Tuple[int, int, int]:
    infected = min(healthy, sick)
    healed = sick // 2
    return healthy - infected, sick - healed + infected, recovered + healed


def sir_run(healthy: int, sick: int, ticks: int) -> List[Tuple[int, int, int]]:
    recovered = 0
    history = []
    for _ in range(ticks):
        healthy, sick, recovered = sir_tick(healthy, sick, recovered)
        history.append((healthy, sick, recovered))
    return history


class SirTicksTask(BaseMathTask):
    TASK_TYPE = "sir_ticks"
    TASK_TYPES = ["recovered", "healthy"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 2}, 2: {"n": 2, "m": 3}, 3: {"n": 3, "m": 3},
        4: {"n": 3, "m": 4}, 5: {"n": 4, "m": 4}, 6: {"n": 5, "m": 4},
        7: {"n": 6, "m": 5}, 8: {"n": 7, "m": 5}, 9: {"n": 8, "m": 5},
        10: {"n": 10, "m": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.sick = 2 * random.randint(1, int(p["m"]))
        self.healthy = self.sick * 3 ** self.n
        self.history = sir_run(self.healthy, self.sick, self.n)
        self.final_healthy, self.final_sick, self.final_recovered = self.history[-1]
        self.answer = self.final_recovered if self.task_type == "recovered" else self.final_healthy
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "recovered" else "s1"
        return texts.t(key, language, healthy=self.healthy, sick=self.sick, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, healthy=healthy, sick=sick, recovered=recovered)
            for index, (healthy, sick, recovered) in enumerate(self.history, 1)
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
