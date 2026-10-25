"""PolarStackTask — стопка поляризаторов с тремя точными долями.

Код 0 оставляет свет, код 1 оставляет целую половину, код 2 гасит свет.
Число пластинок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def polar_trace(light: int, plates: Sequence[int]) -> List[Tuple[int, int]]:
    bright = light
    dark = 0
    trace = []
    for plate in plates:
        if plate == 1:
            bright //= 2
        elif plate == 2:
            if bright:
                dark += 1
            bright = 0
        trace.append((bright, dark))
    return trace


class PolarStackTask(BaseMathTask):
    TASK_TYPE = "polar_stack"
    TASK_TYPES = ["light", "dark"]

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
        self.light = random.randint(4, 16)
        self.plates = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = polar_trace(self.light, self.plates)
        self.final_light = self.trace[-1][0]
        self.dark = self.trace[-1][1]
        self.answer = self.final_light if self.task_type == "light" else self.dark
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(plate) for plate in self.plates)
        key = "s0" if self.task_type == "light" else "s1"
        return texts.t(key, language, n=self.n, light=self.light, plates=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, plate=plate, light=light, dark=dark)
            for index, (plate, (light, dark)) in enumerate(zip(self.plates, self.trace), 1)
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
