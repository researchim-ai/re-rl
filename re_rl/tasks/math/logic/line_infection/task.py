"""LineInfectionTask — заражение соседей в шеренге.

Число дней растёт с уровнем. Больной заражает соседей слева и справа и сам остаётся болен.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def spread_once(infected: List[bool]) -> List[bool]:
    updated = infected[:]
    for index, sick in enumerate(infected):
        if not sick:
            continue
        if index:
            updated[index - 1] = True
        if index + 1 < len(infected):
            updated[index + 1] = True
    return updated


class LineInfectionTask(BaseMathTask):
    TASK_TYPE = "line_infection"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "p": 5}, 2: {"n": 2, "p": 6}, 3: {"n": 3, "p": 7},
        4: {"n": 4, "p": 8}, 5: {"n": 5, "p": 9}, 6: {"n": 6, "p": 10},
        7: {"n": 7, "p": 12}, 8: {"n": 8, "p": 13}, 9: {"n": 9, "p": 15},
        10: {"n": 10, "p": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "count"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.people = max(self.n + 2, int(p["p"]))
        self.infected = [random.random() < 0.35 for _ in range(self.people)]
        if not any(self.infected):
            self.infected[random.randrange(self.people)] = True
        self.days: List[str] = []
        state = self.infected[:]
        for _ in range(self.n):
            state = spread_once(state)
            self.days.append("".join("1" if flag else "0" for flag in state))
        self.answer = self.days[-1].count("1")
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        initial = "".join("1" if flag else "0" for flag in self.infected)
        return texts.t("s0", language, people=self.people, initial=initial, days=self.n)

    def solve(self):
        steps = [
            texts.t("s1", self.language, i=i, bits=bits, count=bits.count("1"))
            for i, bits in enumerate(self.days, 1)
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
