"""LevelDegTask — орбитальное вырождение уровня водорода.

Без учёта спина уровень n вмещает n*n состояний.
Число уровней в списке растёт со сложностью.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def deg_trace(levels: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    biggest = 0
    trace = []
    for level in levels:
        states = level * level
        total += states
        if states > biggest:
            biggest = states
        trace.append((total, biggest))
    return trace


class LevelDegTask(BaseMathTask):
    TASK_TYPE = "level_deg"
    TASK_TYPES = ["states", "biggest"]

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
        self.levels = [random.randint(1, 6) for _ in range(self.n)]
        self.trace = deg_trace(self.levels)
        self.states = self.trace[-1][0]
        self.biggest = self.trace[-1][1]
        self.answer = self.states if self.task_type == "states" else self.biggest
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(level) for level in self.levels)

    def _descr(self, language):
        key = "s0" if self.task_type == "states" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, states=states, biggest=biggest)
            for index, (states, biggest) in enumerate(self.trace, 1)
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
