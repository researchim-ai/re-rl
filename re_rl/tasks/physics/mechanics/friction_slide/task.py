"""FrictionSlideTask — движение с вычитанием трения каждый такт.

Сначала тело проходит путь, равный скорости, затем скорость падает на трение, но не ниже нуля.
Число тактов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def slide_trace(speed: int, frictions: Sequence[int]) -> List[Tuple[int, int]]:
    place = 0
    trace = []
    for friction in frictions:
        place += speed
        speed = max(0, speed - friction)
        trace.append((place, speed))
    return trace


class FrictionSlideTask(BaseMathTask):
    TASK_TYPE = "friction_slide"
    TASK_TYPES = ["place", "speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 6}, 2: {"n": 2, "v": 8}, 3: {"n": 3, "v": 8},
        4: {"n": 4, "v": 10}, 5: {"n": 5, "v": 12}, 6: {"n": 6, "v": 14},
        7: {"n": 7, "v": 16}, 8: {"n": 8, "v": 18}, 9: {"n": 10, "v": 20},
        10: {"n": 12, "v": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.speed0 = random.randint(1, max(2, int(p["v"])))
        self.frictions = [random.randint(1, 4) for _ in range(self.n)]
        self.trace = slide_trace(self.speed0, self.frictions)
        self.place, self.speed = self.trace[-1]
        self.answer = self.place if self.task_type == "place" else self.speed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.frictions)
        key = "s0" if self.task_type == "place" else "s1"
        return texts.t(key, language, speed=self.speed0, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, friction=friction, place=place, speed=speed)
            for index, (friction, (place, speed)) in enumerate(zip(self.frictions, self.trace), 1)
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
