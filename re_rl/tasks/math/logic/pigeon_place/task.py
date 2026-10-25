"""PigeonPlaceTask — размещение голубей по лункам.

Голубей на одного больше, чем лунок, поэтому какая-то лунка получает хотя бы двоих.
Число голубей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def pigeon_trace(holes: int, places: Sequence[int]) -> List[Tuple[int, int, int]]:
    counts = [0] * (holes + 1)
    crowded = 0
    load = 0
    trace = []
    for place in places:
        counts[place] += 1
        if crowded == 0 and counts[place] >= 2:
            crowded = place
        load = max(load, counts[place])
        trace.append((crowded, counts[place], load))
    return trace


class PigeonPlaceTask(BaseMathTask):
    TASK_TYPE = "pigeon_place"
    TASK_TYPES = ["hole", "load"]

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
        self.holes = self.n - 1
        self.places = [random.randint(1, self.holes) for _ in range(self.n)]
        self.trace = pigeon_trace(self.holes, self.places)
        self.hole = self.trace[-1][0]
        self.load = self.trace[-1][2]
        assert self.hole != 0
        self.answer = self.hole if self.task_type == "hole" else self.load
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        places = ", ".join(str(place) for place in self.places)
        key = "s0" if self.task_type == "hole" else "s1"
        return texts.t(key, language, n=self.n, holes=self.holes, places=places)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, place=place, hole=hole, count=count, load=load)
            for index, (place, (hole, count, load)) in enumerate(zip(self.places, self.trace), 1)
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
