"""FirstFitTask — первая подходящая дырка в ленте памяти.

Заявка занимает самый левый сплошной свободный кусок нужной длины.
Если такого нет, заявка отклоняется. Число заявок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def first_fit(tape: int, sizes: Sequence[int]) -> Tuple[int, List[int]]:
    free = [1] * (tape + 1)
    placed = 0
    starts = []
    for size in sizes:
        start = 0
        run = 0
        for cell in range(1, tape + 1):
            if free[cell]:
                run += 1
                if run == size:
                    start = cell - size + 1
                    break
            else:
                run = 0
        if start:
            for cell in range(start, start + size):
                free[cell] = 0
            placed += 1
        starts.append(start)
    return placed, starts


class FirstFitTask(BaseMathTask):
    TASK_TYPE = "first_fit"
    TASK_TYPES = ["placed", "start"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 8},
        9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.tape = self.n * 2
        self.sizes = [random.randint(1, 3) for _ in range(self.n)]
        self.placed, self.starts = first_fit(self.tape, self.sizes)
        self.k = random.randint(1, self.n)
        self.start = self.starts[self.k - 1]
        self.answer = self.placed if self.task_type == "placed" else self.start
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(size) for size in self.sizes)
        key = "s0" if self.task_type == "placed" else "s1"
        return texts.t(key, language, n=self.n, tape=self.tape, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, size=size, start=start)
            for index, (size, start) in enumerate(zip(self.sizes, self.starts), 1)
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
