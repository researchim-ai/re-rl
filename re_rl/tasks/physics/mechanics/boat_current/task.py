"""BoatCurrentTask — скорость лодки по течению и против течения.

Скорость в стоячей воде больше скорости течения, поэтому обе скорости целые и положительные.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BoatCurrentTask(BaseMathTask):
    TASK_TYPE = "boat_current"
    TASK_TYPES = ["downstream", "upstream", "boat", "current"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 4}, 2: {"v": 5}, 3: {"v": 6}, 4: {"v": 8}, 5: {"v": 10},
        6: {"v": 12}, 7: {"v": 14}, 8: {"v": 16}, 9: {"v": 20}, 10: {"v": 24},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["v"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.vc = random.randint(1, limit)
        self.vb = self.vc + random.randint(1, limit)
        self.down = self.vb + self.vc
        self.up = self.vb - self.vc
        self.answer = {
            "downstream": self.down,
            "upstream": self.up,
            "boat": self.vb,
            "current": self.vc,
        }[self.task_type]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "downstream":
            return texts.t("s0", language, vb=self.vb, vc=self.vc)
        if self.task_type == "upstream":
            return texts.t("s1", language, vb=self.vb, vc=self.vc)
        if self.task_type == "boat":
            return texts.t("s2", language, down=self.down, up=self.up)
        return texts.t("s3", language, down=self.down, up=self.up)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        key = {"downstream": "s4", "upstream": "s5", "boat": "s6", "current": "s7"}[self.task_type]
        step = texts.t(key, self.language, vb=self.vb, vc=self.vc, down=self.down, up=self.up)
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
