"""TrafficLightTask — очередь машин перед светофором.

Цикл начинается с зелёного: g тактов пропускают по одной машине, затем r тактов красного.
Число машин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def departure_times(cars: int, green: int, red: int) -> List[int]:
    times = []
    tick = 0
    phase = 0
    cycle = green + red
    while len(times) < cars:
        tick += 1
        if phase < green:
            times.append(tick)
        phase = (phase + 1) % cycle
    return times


class TrafficLightTask(BaseMathTask):
    TASK_TYPE = "traffic_light"
    TASK_TYPES = ["last", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "g": 1, "r": 1}, 2: {"n": 2, "g": 2, "r": 1},
        3: {"n": 3, "g": 2, "r": 2}, 4: {"n": 3, "g": 2, "r": 2},
        5: {"n": 4, "g": 2, "r": 2}, 6: {"n": 5, "g": 3, "r": 2},
        7: {"n": 6, "g": 3, "r": 3}, 8: {"n": 7, "g": 3, "r": 3},
        9: {"n": 8, "g": 3, "r": 3}, 10: {"n": 10, "g": 4, "r": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.green = random.randint(1, max(1, int(p["g"])))
        self.red = random.randint(1, max(1, int(p["r"])))
        self.times = departure_times(self.n, self.green, self.red)
        self.k = random.randint(1, self.n)
        self.last = self.times[-1]
        self.at_k = self.times[self.k - 1]
        self.answer = self.last if self.task_type == "last" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, n=self.n, g=self.green, r=self.red, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, t=tick)
            for index, tick in enumerate(self.times, 1)
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
