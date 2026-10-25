"""DayClashTask — совпадения дней рождения по мере прихода людей.

Пара появляется, когда день встречается снова. Человек считается в компании, если его день не единственный.
Длина списка растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def birthday_trace(days: Sequence[int]) -> List[Tuple[int, int]]:
    counts: Dict[int, int] = {}
    pairs = 0
    shared = 0
    trace = []
    for day in days:
        counts[day] = counts.get(day, 0) + 1
        if counts[day] == 2:
            pairs += 1
            shared += 2
        elif counts[day] > 2:
            pairs += counts[day] - 1
            shared += 1
        trace.append((pairs, shared))
    return trace


class DayClashTask(BaseMathTask):
    TASK_TYPE = "day_clash"
    TASK_TYPES = ["pairs", "shared"]

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
        span = max(2, self.n // 2)
        self.days = [random.randint(1, span) for _ in range(self.n)]
        self.trace = birthday_trace(self.days)
        self.pairs = self.trace[-1][0]
        self.shared = self.trace[-1][1]
        self.answer = self.pairs if self.task_type == "pairs" else self.shared
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(day) for day in self.days)
        key = "s0" if self.task_type == "pairs" else "s1"
        return texts.t(key, language, n=self.n, days=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, day=day, pairs=pairs, shared=shared)
            for index, (day, (pairs, shared)) in enumerate(zip(self.days, self.trace), 1)
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
