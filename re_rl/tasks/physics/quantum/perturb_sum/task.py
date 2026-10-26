"""PerturbSumTask — вторая поправка к энергии уровня ямы.

Энергия уровня равна квадрату номера. Вклад другого уровня — квадрат матричного элемента,
делённый на разность квадратов. Дробь сокращается после каждого слагаемого.
Число связанных уровней растёт со сложностью.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Couple = Tuple[int, int]


def second_trace(level: int, couples: Sequence[Couple]) -> List[Tuple[int, int]]:
    total = Fraction(0)
    base = level * level
    trace = []
    for other, element in couples:
        gap = base - other * other
        if gap == 0:
            raise RuntimeError("level mismatch")
        total += Fraction(element * element, gap)
        trace.append((total.numerator, total.denominator))
    return trace


class PerturbSumTask(BaseMathTask):
    TASK_TYPE = "perturb_sum"
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
        self.level = random.randint(2, 6)
        pool = [item for item in range(1, self.level + self.n + 2) if item != self.level]
        others = random.sample(pool, self.n)
        self.couples = [(other, random.randint(1, 4)) for other in others]
        self.trace = second_trace(self.level, self.couples)
        self.numer = self.trace[-1][0]
        self.denom = self.trace[-1][1]
        self.answer = self.numer if self.task_type == "numer" else self.denom
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{other} {element}" for other, element in self.couples)

    def _descr(self, language):
        key = "s0" if self.task_type == "numer" else "s1"
        return texts.t(key, language, n=self.n, level=self.level, listing=self._listing())

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
