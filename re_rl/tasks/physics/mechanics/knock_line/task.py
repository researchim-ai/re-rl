"""KnockLineTask — цепочка упругих ударов по покоящимся телам.

Ударенное тело летит дальше и бьёт следующее, которое до удара покоилось.
Скорости целые, импульс и энергия каждого удара сходятся.
Число ударов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def knock_trace(masses: Sequence[int], speed: int) -> List[Tuple[int, int]]:
    if len(masses) < 2 or speed == 0:
        raise RuntimeError("hit mismatch")
    trace = []
    for index in range(len(masses) - 1):
        left, right = masses[index], masses[index + 1]
        total = left + right
        if left <= 0 or right <= 0 or total == 0:
            raise RuntimeError("hit mismatch")
        if (2 * left * speed) % total or ((left - right) * speed) % total:
            raise RuntimeError("hit mismatch")
        recoil = (left - right) * speed // total
        passed = 2 * left * speed // total
        if left * speed != left * recoil + right * passed:
            raise RuntimeError("hit mismatch")
        if left * speed * speed != left * recoil * recoil + right * passed * passed:
            raise RuntimeError("hit mismatch")
        trace.append((passed, recoil))
        speed = passed
    return trace


class KnockLineTask(BaseMathTask):
    TASK_TYPE = "knock_line"
    TASK_TYPES = ["passed", "recoil"]

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
        self.speed = random.randint(1, 4)
        self.masses = [random.randint(1, 5)]
        speed = self.speed
        for _ in range(self.n):
            left = self.masses[-1]
            options = []
            for right in range(1, 8):
                total = left + right
                if (2 * left * speed) % total == 0 and ((left - right) * speed) % total == 0:
                    options.append(right)
            unequal = [right for right in options if right != left]
            right = random.choice(unequal or options)
            total = left + right
            speed = 2 * left * speed // total
            self.masses.append(right)
        self.trace = knock_trace(self.masses, self.speed)
        self.passed = self.trace[-1][0]
        self.recoil = self.trace[-1][1]
        self.answer = self.passed if self.task_type == "passed" else self.recoil
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(mass) for mass in self.masses)

    def _descr(self, language):
        key = "s0" if self.task_type == "passed" else "s1"
        return texts.t(key, language, n=self.n, speed=self.speed, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, passed=passed, recoil=recoil)
            for index, (passed, recoil) in enumerate(self.trace, 1)
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
