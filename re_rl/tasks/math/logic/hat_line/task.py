"""HatLineTask — шляпы в шеренге и объявленная чётность.

Последний видит всех впереди и называет сумму их шляп по модулю 2.
Он спасён только если это совпало с его собственной шляпой. Остальные восстанавливают свои шляпы и спасены.
Число людей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rear_parity(hats: Sequence[int]) -> int:
    return sum(hats[:-1]) % 2


def saved_count(hats: Sequence[int]) -> int:
    parity = rear_parity(hats)
    if hats[-1] == parity:
        return len(hats)
    return len(hats) - 1


class HatLineTask(BaseMathTask):
    TASK_TYPE = "hat_line"
    TASK_TYPES = ["saved", "parity"]

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
        self.hats = [random.randint(0, 1) for _ in range(self.n)]
        self.parity = rear_parity(self.hats)
        self.saved = saved_count(self.hats)
        self.answer = self.saved if self.task_type == "saved" else self.parity
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(hat) for hat in self.hats)
        key = "s0" if self.task_type == "saved" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = []
        parity = 0
        for index, hat in enumerate(self.hats[:-1], 1):
            parity = (parity + hat) % 2
            steps.append(texts.t("s2", self.language, i=index, hat=hat, parity=parity))
        steps.append(texts.t(
            "s3", self.language, n=self.n, hat=self.hats[-1], parity=self.parity, saved=self.saved,
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
