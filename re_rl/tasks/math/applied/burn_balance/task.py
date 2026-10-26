"""BurnBalanceTask — целые коэффициенты сгорания.

Множитель подбирается так, чтобы кислород и вода вышли целыми.
Число топлив растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Fuel = Tuple[int, int]


def burn_need(fuels: Sequence[Fuel]) -> List[Tuple[int, int]]:
    oxygen = 0
    water = 0
    trace = []
    for carbon, hydrogen in fuels:
        if hydrogen % 4 == 0:
            factor = 1
        elif hydrogen % 2 == 0:
            factor = 2
        else:
            factor = 4
        oxygen += factor * carbon + factor * hydrogen // 4
        water += factor * hydrogen // 2
        trace.append((oxygen, water))
    return trace


class BurnBalanceTask(BaseMathTask):
    TASK_TYPE = "burn_balance"
    TASK_TYPES = ["oxygen", "water"]

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
        self.fuels = [(random.randint(1, 5), random.randint(0, 10)) for _ in range(self.n)]
        self.trace = burn_need(self.fuels)
        self.oxygen = self.trace[-1][0]
        self.water = self.trace[-1][1]
        self.answer = self.oxygen if self.task_type == "oxygen" else self.water
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{carbon} {hydrogen}" for carbon, hydrogen in self.fuels)

    def _descr(self, language):
        key = "s0" if self.task_type == "oxygen" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, oxygen=oxygen, water=water)
            for index, (oxygen, water) in enumerate(self.trace, 1)
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
