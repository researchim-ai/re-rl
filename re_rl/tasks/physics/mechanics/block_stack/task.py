"""BlockStackTask — стопка блоков и момент массы относительно пола.

Число блоков растёт с уровнем. Толщины чётные, поэтому высота центра каждого блока целая.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BlockStackTask(BaseMathTask):
    TASK_TYPE = "block_stack"
    TASK_TYPES = ["mass", "moment"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 5, "t": 3}, 2: {"n": 2, "m": 6, "t": 4},
        3: {"n": 3, "m": 6, "t": 4}, 4: {"n": 3, "m": 8, "t": 5},
        5: {"n": 4, "m": 8, "t": 5}, 6: {"n": 5, "m": 10, "t": 6},
        7: {"n": 6, "m": 10, "t": 6}, 8: {"n": 7, "m": 12, "t": 7},
        9: {"n": 8, "m": 12, "t": 8}, 10: {"n": 10, "m": 15, "t": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.masses: List[int] = [random.randint(1, int(p["m"])) for _ in range(self.n)]
        self.thickness: List[int] = [2 * random.randint(1, int(p["t"])) for _ in range(self.n)]
        centers: List[int] = []
        floor = 0
        for thickness in self.thickness:
            centers.append(floor + thickness // 2)
            floor += thickness
        self.centers = centers
        self.parts = [mass * center for mass, center in zip(self.masses, self.centers)]
        self.total_mass = sum(self.masses)
        self.moment = sum(self.parts)
        self.answer = self.total_mass if self.task_type == "mass" else self.moment
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self, language):
        parts = [
            texts.t("s2", language, i=i, mass=mass, thickness=thickness)
            for i, (mass, thickness) in enumerate(zip(self.masses, self.thickness), 1)
        ]
        return " ".join(parts)

    def _descr(self, language):
        key = "s0" if self.task_type == "mass" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing(language))

    def solve(self):
        steps = []
        for index, (mass, center, part) in enumerate(zip(self.masses, self.centers, self.parts), 1):
            steps.append(texts.t("s3", self.language, i=index, mass=mass, center=center, part=part))
        if self.task_type == "mass":
            steps.append(texts.t("s4", self.language, total=self.total_mass))
        else:
            steps.append(texts.t("s5", self.language, moment=self.moment))
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
