"""ResistorLadderTask — лестница из последовательных и параллельных секций.

Секция сначала добавляет сопротивление последовательно, затем ставит результат параллельно.
Числа подобраны так, что параллельная формула даёт целое. Число секций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Section = Tuple[int, int]


def choose_section(resistance: int) -> Section:
    series = resistance
    parallel = 2 * resistance
    for _ in range(12):
        series_try = random.randint(1, 6)
        joined = resistance + series_try
        divisors = [item for item in range(1, joined) if joined % item == 0]
        gap = random.choice(divisors)
        target = joined - gap
        parallel_try = target * joined // gap
        denom = joined + parallel_try
        if denom > 0 and (joined * parallel_try) % denom == 0:
            if joined * parallel_try // denom == target and target > 0:
                return series_try, parallel_try
    return series, parallel


def ladder_trace(start: int, sections: Sequence[Section]) -> List[int]:
    resistance = start
    trace = []
    for series, parallel in sections:
        joined = resistance + series
        resistance = joined * parallel // (joined + parallel)
        trace.append(resistance)
    return trace


class ResistorLadderTask(BaseMathTask):
    TASK_TYPE = "resistor_ladder"
    TASK_TYPES = ["equivalent", "peak"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(2, 8)
        self.sections = []
        resistance = self.start
        for _ in range(self.n):
            series, parallel = choose_section(resistance)
            self.sections.append((series, parallel))
            joined = resistance + series
            resistance = joined * parallel // (joined + parallel)
        self.trace = ladder_trace(self.start, self.sections)
        self.equivalent = self.trace[-1]
        self.peak = max([self.start, *self.trace])
        self.answer = self.equivalent if self.task_type == "equivalent" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{series}, {parallel}" for series, parallel in self.sections)
        key = "s0" if self.task_type == "equivalent" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, series=series, parallel=parallel, value=value)
            for index, ((series, parallel), value) in enumerate(zip(self.sections, self.trace), 1)
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
