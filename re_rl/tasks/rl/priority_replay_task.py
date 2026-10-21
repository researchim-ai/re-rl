"""PriorityReplayTask — вероятность пропорционального приоритетного семплирования.

P(i) = p_i / сумма p. Номера с 1. При равном максимуме берётся меньший номер.
"""

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
        ru = language == "ru"
        shown = ", ".join(f"{i + 1}: {value}" for i, value in enumerate(self.priorities))
        rule = ((f"Приоритеты переходов, номера с 1: {shown}. "
                 f"Вероятность номера равна его приоритету, делённому на сумму. "
                 f"Номер с наибольшим приоритетом при равенстве — меньший.") if ru else
                (f"Transition priorities, indices start at 1: {shown}. "
                 f"The probability of an index is its priority divided by the sum. "
                 f"The maximum priority breaks ties toward the smaller index."))
        if self.task_type == "probability":
            ask = ((f"Найдите вероятность номера {self.index + 1}. Ответ — целое или несократимая дробь.")
                   if ru else
                   (f"Find the probability of index {self.index + 1}. "
                    f"Answer with an integer or a reduced fraction."))
        else:
            ask = (("Какой номер имеет наибольший приоритет?" if ru else
                    "Which index has the greatest priority?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = str(self.argmax) if self.task_type == "argmax" else fmt_fraction(self.probability)
        step = ((f"Вероятность номера {self.index + 1} равна {fmt_fraction(self.probability)}, "
                 f"максимум у номера {self.argmax}.") if ru else
                (f"Probability of index {self.index + 1} is {fmt_fraction(self.probability)}, "
                 f"the maximum is at index {self.argmax}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
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
