"""BayesUpdatesTask — цепочка обновлений с целым процентом гипотезы.

Каждое свидетельство умножает шансы на целое отношение. Пара подбирается так, чтобы процент снова был целым.
Число свидетельств растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _pick_ratio(favor: int, against: int) -> Tuple[int, int, int]:
    for _ in range(40):
        yes = random.randint(1, 4)
        no = random.randint(1, 4)
        num = favor * yes
        den = against * no
        total = num + den
        if total and (100 * num) % total == 0:
            return yes, no, (100 * num) // total
    return 1, 1, (100 * favor) // (favor + against)


class BayesUpdatesTask(BaseMathTask):
    TASK_TYPE = "bayes_updates"
    TASK_TYPES = ["percent", "increases"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(1, 99)
        favor, against = self.start, 100 - self.start
        self.updates: List[Dict[str, int]] = []
        self.increases = 0
        for _ in range(self.n):
            old = (100 * favor) // (favor + against)
            yes, no, new = _pick_ratio(favor, against)
            num = favor * yes
            den = against * no
            if new > old:
                self.increases += 1
            divisor = math.gcd(num, den)
            favor, against = num // divisor, den // divisor
            self.updates.append({"yes": yes, "no": no, "old": old, "new": new})
        self.percent = (100 * favor) // (favor + against)
        self.favor, self.against = favor, against
        self.answer = self.percent if self.task_type == "percent" else self.increases
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = [
            texts.t("s2", language, i=i, yes=item["yes"], no=item["no"])
            for i, item in enumerate(self.updates, 1)
        ]
        key = "s0" if self.task_type == "percent" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=" ".join(parts))

    def solve(self):
        steps = [
            texts.t("s3", self.language, i=i, yes=item["yes"], no=item["no"], old=item["old"], new=item["new"])
            for i, item in enumerate(self.updates, 1)
        ]
        steps.append(texts.t("s4", self.language, percent=self.percent, increases=self.increases))
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
