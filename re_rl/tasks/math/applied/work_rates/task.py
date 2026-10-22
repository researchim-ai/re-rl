"""WorkRatesTask — совместная работа двух исполнителей.

Если первый справляется за a дней, а второй за b, вместе им нужно ab/(a+b) дней.
Пары (a, b) выбираются так, чтобы это число было целым.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _work_pairs(limit: int) -> List[Tuple[int, int, int]]:
    pairs = []
    for together in range(1, limit + 1):
        for alone in range(together + 1, together * 4 + 1):
            gap = alone - together
            if (alone * together) % gap != 0:
                continue
            partner = (alone * together) // gap
            if partner >= alone:
                pairs.append((alone, partner, together))
    return pairs


class WorkRatesTask(BaseMathTask):
    TASK_TYPE = "work_rates"
    TASK_TYPES = ["together", "partner"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 6}, 4: {"n": 8}, 5: {"n": 10},
        6: {"n": 12}, 7: {"n": 14}, 8: {"n": 16}, 9: {"n": 18}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        pairs = _work_pairs(int(p["n"]))
        unequal = [item for item in pairs if item[0] != item[1]]
        self.a, self.b, self.together = random.choice(unequal or pairs)
        self.answer = self.together if self.task_type == "together" else self.b
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "together":
            return texts.t("s0", language, a=self.a, b=self.b)
        return texts.t("s1", language, together=self.together, a=self.a)

    def solve(self):
        if self.task_type == "together":
            step = texts.t("s2", self.language, a=self.a, b=self.b, together=self.together)
        else:
            step = texts.t("s3", self.language, together=self.together, a=self.a, b=self.b)
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
