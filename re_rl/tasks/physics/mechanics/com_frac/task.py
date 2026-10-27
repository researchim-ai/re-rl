"""ComFracTask — центр масс при добавлении тел по одному.

Момент и масса складываются, дробь сокращается после каждого тела.
Число тел растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Body = Tuple[int, int]


def com_trace(bodies: Sequence[Body]) -> List[Tuple[int, int]]:
    mass = 0
    moment = 0
    trace = []
    for weight, place in bodies:
        if weight <= 0:
            raise RuntimeError("mass mismatch")
        mass += weight
        moment += weight * place
        gap = math.gcd(abs(moment), mass)
        trace.append((moment // gap, mass // gap))
    return trace


class ComFracTask(BaseMathTask):
    TASK_TYPE = "com_frac"
    TASK_TYPES = ["numer", "denom"]

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
        self.bodies = [
            (random.randint(1, 5), random.randint(-4, 6)) for _ in range(self.n)
        ]
        self.trace = com_trace(self.bodies)
        self.numer = self.trace[-1][0]
        self.denom = self.trace[-1][1]
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{weight} {place}" for weight, place in self.bodies)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, numer=numer, denom=denom)
            for index, (numer, denom) in enumerate(self.trace, 1)
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
