"""GradClipTask — шаг с обрезкой градиента.

Градиент ограничивается отрезком от минус предела до предела, затем вычитается из веса.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def clip_trace(start: int, gradients: Sequence[int], limit: int) -> List[Tuple[int, int, int]]:
    weight = start
    clips = 0
    trace = []
    for gradient in gradients:
        clipped = gradient
        if clipped > limit:
            clipped = limit
        elif clipped < -limit:
            clipped = -limit
        if clipped != gradient:
            clips += 1
        weight -= clipped
        trace.append((clipped, weight, clips))
    return trace


class GradClipTask(BaseMathTask):
    TASK_TYPE = "grad_clip"
    TASK_TYPES = ["weight", "clips"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "c": 1, "m": 4}, 2: {"n": 3, "c": 1, "m": 4},
        3: {"n": 4, "c": 2, "m": 5}, 4: {"n": 5, "c": 2, "m": 5},
        5: {"n": 6, "c": 2, "m": 6}, 6: {"n": 7, "c": 3, "m": 6},
        7: {"n": 8, "c": 3, "m": 7}, 8: {"n": 10, "c": 3, "m": 7},
        9: {"n": 12, "c": 4, "m": 8}, 10: {"n": 14, "c": 4, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.limit = max(1, int(p["c"]))
        span = max(self.limit + 1, int(p["m"]))
        self.start = random.randint(-span, span)
        self.gradients = [random.randint(-span, span) for _ in range(self.n)]
        self.trace = clip_trace(self.start, self.gradients, self.limit)
        _, self.weight, self.clips = self.trace[-1]
        self.answer = self.weight if self.task_type == "weight" else self.clips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(gradient) for gradient in self.gradients)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, limit=self.limit, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, raw=raw, clipped=clipped, weight=weight, clips=clips)
            for index, (raw, (clipped, weight, clips)) in enumerate(zip(self.gradients, self.trace), 1)
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
