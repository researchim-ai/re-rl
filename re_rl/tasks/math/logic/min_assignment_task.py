"""MinAssignmentTask — задача о назначениях.

Каждый работник получает ровно одну работу. Среди оптимальных назначений
берётся лексикографически первая последовательность номеров работ.
Номера работников и работ с 1.
"""

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def min_assignment(cost: Sequence[Sequence[int]]) -> Tuple[int, Tuple[int, ...]]:
    best = None
    best_perm = None
    for perm in permutations(range(len(cost))):
        total = sum(cost[worker][job] for worker, job in enumerate(perm))
        if best is None or total < best:
            best = total
            best_perm = perm
    return best, best_perm


class MinAssignmentTask(BaseMathTask):
    TASK_TYPE = "min_assignment"
    TASK_TYPES = ["cost", "job"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mag": 6}, 2: {"n": 3, "mag": 8}, 3: {"n": 3, "mag": 9},
        4: {"n": 4, "mag": 9}, 5: {"n": 4, "mag": 12}, 6: {"n": 4, "mag": 12},
        7: {"n": 5, "mag": 15}, 8: {"n": 5, "mag": 15}, 9: {"n": 6, "mag": 18},
        10: {"n": 6, "mag": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.mag = int(p["mag"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.cost = [
            [random.randint(1, self.mag) for _ in range(self.n)]
            for _ in range(self.n)
        ]
        self.best, self.perm = min_assignment(self.cost)
        self.worker = random.randrange(self.n)
        self.job = self.perm[self.worker] + 1
        self.answer = self.best if self.task_type == "cost" else self.job
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _matrix(self) -> str:
        return "; ".join(
            f"{i + 1}: {' '.join(map(str, row))}" for i, row in enumerate(self.cost)
        )

    def _descr(self, language):
        ru = language == "ru"
        rule = ((f"Квадрат стоимостей, строка — работник, столбец — работа, номера с 1: {self._matrix()}. "
                 f"Каждый работник получает одну работу, каждая работа достаётся одному. "
                 f"Среди назначений минимальной стоимости берётся лексикографически первая последовательность работ.")
                if ru else
                (f"Cost square, a row is a worker and a column is a job, indices start at 1: {self._matrix()}. "
                 f"Each worker gets one job, and each job goes to one worker. "
                 f"Among minimum-cost assignments, take the lexicographically first job sequence."))
        if self.task_type == "cost":
            ask = ("Найдите минимальную стоимость." if ru else "Find the minimum cost.")
        else:
            ask = ((f"Какую работу получает работник {self.worker + 1} в этом назначении?") if ru else
                   (f"Which job does worker {self.worker + 1} receive in that assignment?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        jobs = ", ".join(str(job + 1) for job in self.perm)
        step = ((f"Стоимость {self.best}, работы по работникам: {jobs}.") if ru else
                (f"Cost {self.best}, jobs by worker: {jobs}."))
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
