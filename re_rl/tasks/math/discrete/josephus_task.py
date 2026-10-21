"""JosephusTask — последний оставшийся в круге.

Люди занумерованы с 1. Счёт каждый раз начинается со следующего после выбывшего
и идёт по часовой стрелке. Выбывает каждый k-й из ещё стоящих в круге.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def josephus(n: int, k: int) -> Tuple[int, List[int]]:
    people = list(range(1, n + 1))
    index = 0
    eliminated: List[int] = []
    while len(people) > 1:
        index = (index + k - 1) % len(people)
        eliminated.append(people.pop(index))
        index %= len(people)
    return people[0], eliminated


class JosephusTask(BaseMathTask):
    TASK_TYPE = "josephus"
    TASK_TYPES = ["survivor"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6, "k": 3}, 2: {"n": 8, "k": 4}, 3: {"n": 10, "k": 5},
        4: {"n": 12, "k": 6}, 5: {"n": 15, "k": 7}, 6: {"n": 18, "k": 8},
        7: {"n": 22, "k": 10}, 8: {"n": 26, "k": 12}, 9: {"n": 30, "k": 14},
        10: {"n": 36, "k": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "survivor"
        self.augment = augment
        self.n = random.randint(1, int(p["n"]))
        self.k = random.randint(1, int(p["k"]))
        self.answer, self.eliminated = josephus(self.n, self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"В круге {self.n} человек, номера от 1 до {self.n}. "
                 f"Счёт начинается с номера 1 и идёт по возрастанию, после {self.n} снова к меньшим. "
                 f"Выбывает каждый {self.k}-й из ещё стоящих, следующий счёт начинается со следующего номера. "
                 f"Какой номер останется последним?") if ru else
                (f"There are {self.n} people in a circle, numbered 1 through {self.n}. "
                 f"Counting starts at 1 and increases, wrapping after {self.n}. "
                 f"Every {self.k}-th person still standing is eliminated, and the next count starts at the next number. "
                 f"Which number remains last?"))

    def solve(self):
        ru = self.language == "ru"
        gone = ", ".join(map(str, self.eliminated)) if self.eliminated else ("—" if ru else "-")
        step = ((f"Порядок выбывания: {gone}. Остаётся {self.answer}.") if ru else
                (f"Elimination order: {gone}. {self.answer} remains."))
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
