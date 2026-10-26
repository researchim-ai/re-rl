"""SpinAddTask — последовательное сложение спинов 1/2.

Число способов получить проекцию m после нового спина складывается из прежних m-1 и m+1.
Число добавленных спинов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def multiplet_trace(spins: int) -> List[Tuple[int, int]]:
    ways = {0: 1}
    trace = []
    for _ in range(spins):
        updated: Dict[int, int] = {}
        for projection, count in ways.items():
            updated[projection + 1] = updated.get(projection + 1, 0) + count
            updated[projection - 1] = updated.get(projection - 1, 0) + count
        ways = updated
        middle = min(projection for projection in ways if projection >= 0)
        trace.append((ways[middle], sum(ways.values())))
    return trace


class SpinAddTask(BaseMathTask):
    TASK_TYPE = "spin_add"
    TASK_TYPES = ["middle", "states"]

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
        self.trace = multiplet_trace(self.n)
        self.middle = self.trace[-1][0]
        self.states = self.trace[-1][1]
        self.answer = self.middle if self.task_type == "middle" else self.states
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "middle" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, middle=middle, states=states)
            for index, (middle, states) in enumerate(self.trace, 1)
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
