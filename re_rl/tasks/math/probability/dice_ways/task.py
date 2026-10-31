"""DiceWaysTask — число исходов суммы двух одинаковых кубиков.

Грани 1..f. Для суммы s число способов равно числу пар (a, b) с a + b = s.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ways_for_sum(faces: int, total: int) -> int:
    return sum(1 for a in range(1, faces + 1) for b in range(1, faces + 1) if a + b == total)


class DiceWaysTask(BaseMathTask):
    TASK_TYPE = "dice_ways"
    TASK_TYPES = ["ways", "smaller_sum"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"f": 4}, 2: {"f": 6}, 3: {"f": 6}, 4: {"f": 8}, 5: {"f": 8},
        6: {"f": 10}, 7: {"f": 12}, 8: {"f": 12}, 9: {"f": 16}, 10: {"f": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.faces = random.randint(2, int(p["f"]))
        if self.task_type == "ways":
            self.total = random.randint(2, 2 * self.faces)
            self.ways = ways_for_sum(self.faces, self.total)
            self.answer = self.ways
        else:
            self.ways = random.randint(1, self.faces)
            self.total = self.ways + 1
            self.answer = self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "ways":
            return texts.t("s0", language, faces=self.faces, total=self.total)
        return texts.t("s1", language, faces=self.faces, ways=self.ways)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "ways":
            step = texts.t("s2", self.language, faces=self.faces, total=self.total, ways=self.ways)
        else:
            high = 2 * self.faces + 1 - self.ways
            if self.ways == self.faces:
                step = texts.t("s4", self.language, ways=self.ways, answer=self.total)
            else:
                step = texts.t(
                    "s3", self.language, ways=self.ways, low=self.total, high=high, answer=self.total,
                )
        self.solution_steps = [step, texts.common("answer_line", self.language, answer=self.answer)]
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
