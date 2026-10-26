"""ScreenCountTask — положительные тесты больных и здоровых.

Доли заданы так, что число людей делится нацело и ответ остаётся целым.
Число клиник растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Clinic = Tuple[int, int]


def screen_trace(clinics: Sequence[Clinic], hit: int, miss: int, den: int) -> List[Tuple[int, int]]:
    true_pos = 0
    false_pos = 0
    trace = []
    for sick, healthy in clinics:
        true_pos += sick * hit // den
        false_pos += healthy * miss // den
        trace.append((true_pos, false_pos))
    return trace


class ScreenCountTask(BaseMathTask):
    TASK_TYPE = "screen_count"
    TASK_TYPES = ["true_pos", "false_pos"]

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
        self.den = random.choice((2, 4, 5))
        self.hit = random.randint(1, self.den)
        self.miss = random.randint(0, self.hit - 1)
        self.clinics = [
            (self.den * random.randint(0, 4), self.den * random.randint(0, 5))
            for _ in range(self.n)
        ]
        self.trace = screen_trace(self.clinics, self.hit, self.miss, self.den)
        self.true_pos = self.trace[-1][0]
        self.false_pos = self.trace[-1][1]
        self.answer = self.true_pos if self.task_type == "true_pos" else self.false_pos
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{sick} {healthy}" for sick, healthy in self.clinics)

    def _descr(self, language):
        key = "s0" if self.task_type == "true_pos" else "s1"
        return texts.t(
            key, language, n=self.n, listing=self._listing(),
            den=self.den, hit=self.hit, miss=self.miss,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, true_pos=true_pos, false_pos=false_pos)
            for index, (true_pos, false_pos) in enumerate(self.trace, 1)
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
