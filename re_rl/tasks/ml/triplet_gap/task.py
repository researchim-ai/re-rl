"""TripletGapTask — запас между своим и чужим примером.

Запас — модуль разности с чужим минус модуль разности со своим. Нарушение, если запас меньше 1.
Число троек растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Triple = Tuple[int, int, int]


def triplet_trace(rows: Sequence[Triple], margin: int = 1) -> List[Tuple[int, int, int]]:
    bad = 0
    worst: Optional[int] = None
    trace = []
    for anchor, positive, negative in rows:
        gap = abs(anchor - negative) - abs(anchor - positive)
        if gap < margin:
            bad += 1
        if worst is None or gap < worst:
            worst = gap
        trace.append((gap, bad, worst))
    return trace


class TripletGapTask(BaseMathTask):
    TASK_TYPE = "triplet_gap"
    TASK_TYPES = ["bad", "worst"]
    MARGIN = 1

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
        self.rows = [
            (random.randint(0, 9), random.randint(0, 9), random.randint(0, 9))
            for _ in range(self.n)
        ]
        self.trace = triplet_trace(self.rows, self.MARGIN)
        self.bad = self.trace[-1][1]
        self.worst = self.trace[-1][2]
        self.answer = self.bad if self.task_type == "bad" else self.worst
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{anchor} {positive} {negative}" for anchor, positive, negative in self.rows)
        key = "s0" if self.task_type == "bad" else "s1"
        return texts.t(key, language, n=self.n, rows=shown, margin=self.MARGIN)

    def solve(self):
        steps = []
        for index, ((anchor, positive, negative), (gap, bad, worst)) in enumerate(zip(self.rows, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, anchor=anchor, positive=positive,
                negative=negative, gap=gap, bad=bad, worst=worst,
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
