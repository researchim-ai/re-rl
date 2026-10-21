"""PriorityReplayTask — вероятность пропорционального приоритетного семплирования.

P(i) = p_i / сумма p. Номера с 1. При равном максимуме берётся меньший номер.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def replay_parts(priorities: List[int], index: int) -> Tuple[Fraction, int]:
    total = sum(priorities)
    best = max(priorities)
    chosen = min(i for i, value in enumerate(priorities) if value == best) + 1
    return Fraction(priorities[index], total), chosen


class PriorityReplayTask(BaseMathTask):
    TASK_TYPE = "priority_replay"
    TASK_TYPES = ["probability", "argmax"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "mag": 4}, 2: {"n": 3, "mag": 5}, 3: {"n": 3, "mag": 6},
        4: {"n": 4, "mag": 6}, 5: {"n": 4, "mag": 8}, 6: {"n": 5, "mag": 8},
        7: {"n": 5, "mag": 10}, 8: {"n": 6, "mag": 10}, 9: {"n": 6, "mag": 12},
        10: {"n": 7, "mag": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.priorities = [random.randint(1, self.mag) for _ in range(self.n)]
        if random.random() < 0.35:
            top = max(self.priorities)
            self.priorities[random.randrange(self.n)] = top
        self.index = random.randrange(self.n)
        self.probability, self.argmax = replay_parts(self.priorities, self.index)
        self.answer = self.probability if self.task_type == "probability" else Fraction(self.argmax)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{i + 1}: {value}" for i, value in enumerate(self.priorities))
        rule = ((texts.t('s0', language, shown=shown)))
        if self.task_type == "probability":
            ask = ((texts.t('s2', language, v0=self.index + 1)))
        else:
            ask = (((texts.t('s3', language))))
        return f"{rule} {ask}"

    def solve(self):
        shown = str(self.argmax) if self.task_type == "argmax" else fmt_fraction(self.probability)
        step = ((texts.t('s1', self.language, v0=self.index + 1, v1=fmt_fraction(self.probability), argmax=self.argmax)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "argmax":
            return U.verify_int(prediction, self.argmax)
        return verify_fraction(prediction, self.probability)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
