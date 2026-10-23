"""RhoCycleTask — цикл в функциональном графе алгоритмом Флойда.

У каждой вершины ровно один исходящий переход. Черепаха делает шаг, заяц два.
Поиск встречи и длина цикла линейны по числу вершин.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rho_cycle(succ: Sequence[int], start: int) -> Tuple[int, int]:
    tortoise = start
    hare = start
    guard = 0
    limit = len(succ) * 4
    while True:
        tortoise = succ[tortoise]
        hare = succ[succ[hare]]
        guard += 1
        if tortoise == hare or guard > limit:
            break
    meet = tortoise
    length = 1
    cursor = succ[meet]
    while cursor != meet and length <= len(succ):
        cursor = succ[cursor]
        length += 1
    return meet, length


class RhoCycleTask(BaseMathTask):
    TASK_TYPE = "rho_cycle"
    TASK_TYPES = ["cycle", "meet"]

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
        self.succ = [0] + [random.randint(1, self.n) for _ in range(self.n)]
        self.start = 1
        self.meet, self.cycle = rho_cycle(self.succ, self.start)
        self.answer = self.cycle if self.task_type == "cycle" else self.meet
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{node}-{self.succ[node]}" for node in range(1, self.n + 1))
        key = "s0" if self.task_type == "cycle" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, start=self.start)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=node, nxt=self.succ[node])
            for node in range(1, self.n + 1)
        ]
        steps.append(texts.t("s3", self.language, meet=self.meet, cycle=self.cycle))
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
