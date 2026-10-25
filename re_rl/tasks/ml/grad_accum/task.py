"""GradAccumTask — шаг веса после суммы двух готовых градиентов.

Нечётный шаг только копит сумму. Чётный вычитает её из веса и обнуляет накопитель.
Число градиентов чётно и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def accum_trace(start: int, grads: Sequence[int]) -> List[Tuple[int, int, int]]:
    weight = start
    running = 0
    trace = []
    for index, grad in enumerate(grads, 1):
        running += grad
        applied = 0
        if index % 2 == 0:
            applied = running
            weight -= running
            running = 0
        trace.append((applied, weight, running))
    return trace


class GradAccumTask(BaseMathTask):
    TASK_TYPE = "grad_accum"
    TASK_TYPES = ["weight", "pair"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 6}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 8}, 7: {"n": 10}, 8: {"n": 12},
        9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = random.randint(0, 5)
        self.grads = [random.randint(-3, 3) for _ in range(self.n)]
        self.trace = accum_trace(self.start, self.grads)
        self.weight = self.trace[-1][1]
        self.pair = self.trace[-1][0]
        self.answer = self.weight if self.task_type == "weight" else self.pair
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(grad) for grad in self.grads)
        key = "s0" if self.task_type == "weight" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, grads=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, grad=grad, applied=applied, weight=weight, running=running)
            for index, (grad, (applied, weight, running)) in enumerate(zip(self.grads, self.trace), 1)
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
