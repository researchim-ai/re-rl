"""SumConvTask — свёртка двух дискретных законов.

К закону первой величины по очереди прибавляется каждый атом второй.
Масса перемножается, ненормированное среднее складывается.
Число атомов второй величины растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Atom = Tuple[int, int]


def conv_trace(left: Sequence[Atom], right: Sequence[Atom], target: int) -> List[Tuple[int, int]]:
    mass_x = 0
    moment_x = 0
    for value, weight in left:
        if weight <= 0:
            raise RuntimeError("conv mismatch")
        mass_x += weight
        moment_x += value * weight
    if mass_x <= 0:
        raise RuntimeError("conv mismatch")
    dist: Dict[int, int] = {}
    mass_y = 0
    moment_y = 0
    trace = []
    for value, weight in right:
        if weight <= 0:
            raise RuntimeError("conv mismatch")
        for base, base_weight in left:
            dist[base + value] = dist.get(base + value, 0) + base_weight * weight
        mass_y += weight
        moment_y += value * weight
        total = mass_x * mass_y
        moment = moment_x * mass_y + mass_x * moment_y
        if sum(dist.values()) != total or sum(point * count for point, count in dist.items()) != moment:
            raise RuntimeError("conv mismatch")
        trace.append((dist.get(target, 0), moment))
    return trace


class SumConvTask(BaseMathTask):
    TASK_TYPE = "sum_conv"
    TASK_TYPES = ["hit", "moment"]

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
        self.left = [(value, random.randint(1, 3)) for value in (0, 1, 2)]
        self.right = [(random.randint(0, 3), random.randint(1, 3)) for _ in range(self.n)]
        self.target = self.left[0][0] + self.right[0][0]
        self.trace = conv_trace(self.left, self.right, self.target)
        self.hit = self.trace[-1][0]
        self.moment = self.trace[-1][1]
        self.answer = self.hit if self.task_type == "hit" else self.moment
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self, atoms: Sequence[Atom]) -> str:
        return "; ".join(f"{value} {weight}" for value, weight in atoms)

    def _descr(self, language):
        key = "s0" if self.task_type == "hit" else "s1"
        return texts.t(
            key, language, n=self.n, target=self.target,
            left=self._listing(self.left), right=self._listing(self.right),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, hit=hit, moment=moment)
            for index, (hit, moment) in enumerate(self.trace, 1)
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
