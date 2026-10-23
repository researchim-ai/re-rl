"""ModeTrackTask — мода потока чисел.

При равной частоте берётся меньшее значение. Считается конечная мода и число её смен.
Длина потока растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def mode_trace(values: Sequence[int]) -> Tuple[List[Tuple[int, int]], int]:
    counts = {}
    modes = []
    for value in values:
        counts[value] = counts.get(value, 0) + 1
        best_value = None
        best_count = -1
        for item, count in counts.items():
            if count > best_count or (count == best_count and item < best_value):
                best_value = item
                best_count = count
        modes.append((best_value, best_count))
    switches = sum(modes[index][0] != modes[index - 1][0] for index in range(1, len(modes)))
    return modes, switches


class ModeTrackTask(BaseMathTask):
    TASK_TYPE = "mode_track"
    TASK_TYPES = ["mode", "switches"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 2}, 2: {"n": 3, "m": 2}, 3: {"n": 4, "m": 3},
        4: {"n": 5, "m": 3}, 5: {"n": 6, "m": 3}, 6: {"n": 8, "m": 4},
        7: {"n": 10, "m": 4}, 8: {"n": 12, "m": 4}, 9: {"n": 14, "m": 5},
        10: {"n": 16, "m": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.values = [random.randint(0, limit) for _ in range(self.n)]
        self.modes, self.switches = mode_trace(self.values)
        self.mode, self.count = self.modes[-1]
        self.answer = self.mode if self.task_type == "mode" else self.switches
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "mode" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, value=value, mode=mode, count=count)
            for index, (value, (mode, count)) in enumerate(zip(self.values, self.modes), 1)
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
