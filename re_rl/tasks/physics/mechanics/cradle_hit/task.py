"""CradleHitTask — удар группы шаров по неподвижным группам.

Сколько шаров улетает, равно меньшему из числа летящих и числа стоящих в группе.
Дальше летит только улетевшая группа. Число групп растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cradle_trace(moving: int, clusters: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    trace = []
    for cluster in clusters:
        fly = moving if moving < cluster else cluster
        total += fly
        moving = fly
        trace.append((fly, moving, total))
    return trace


class CradleHitTask(BaseMathTask):
    TASK_TYPE = "cradle_hit"
    TASK_TYPES = ["fly", "total"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.moving = random.randint(1, 6)
        self.clusters = [random.randint(1, 6) for _ in range(self.n)]
        self.trace = cradle_trace(self.moving, self.clusters)
        self.fly, _, self.total = self.trace[-1]
        self.answer = self.fly if self.task_type == "fly" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(cluster) for cluster in self.clusters)
        key = "s0" if self.task_type == "fly" else "s1"
        return texts.t(key, language, moving=self.moving, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, cluster=cluster, fly=fly, moving=moving, total=total)
            for index, (cluster, (fly, moving, total)) in enumerate(zip(self.clusters, self.trace), 1)
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
