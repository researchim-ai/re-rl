"""BeamLoadTask — моменты сил на балке с опорой в нуле.

Момент груза — сила, умноженная на координату. Положительная координата справа.
Число грузов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Load = Tuple[int, int]


def beam_trace(loads: Sequence[Load], limit: int) -> List[Tuple[int, int]]:
    moment = 0
    tip = 0
    trace = []
    for index, (force, place) in enumerate(loads, 1):
        moment += force * place
        if tip == 0 and abs(moment) >= limit:
            tip = index
        trace.append((moment, tip))
    return trace


class BeamLoadTask(BaseMathTask):
    TASK_TYPE = "beam_load"
    TASK_TYPES = ["moment", "tip"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 5}, 3: {"n": 4, "m": 6},
        4: {"n": 5, "m": 6}, 5: {"n": 6, "m": 8}, 6: {"n": 7, "m": 8},
        7: {"n": 8, "m": 10}, 8: {"n": 10, "m": 12}, 9: {"n": 12, "m": 14},
        10: {"n": 14, "m": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.limit = max(1, int(p["m"]))
        self.loads = [
            (random.randint(1, 4), random.randint(-3, 3))
            for _ in range(self.n)
        ]
        self.trace = beam_trace(self.loads, self.limit)
        self.moment, self.tip = self.trace[-1]
        self.answer = self.moment if self.task_type == "moment" else self.tip
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{force}, {place}" for force, place in self.loads)
        key = "s0" if self.task_type == "moment" else "s1"
        return texts.t(key, language, n=self.n, limit=self.limit, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, moment=moment, tip=tip)
            for index, (moment, tip) in enumerate(self.trace, 1)
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
