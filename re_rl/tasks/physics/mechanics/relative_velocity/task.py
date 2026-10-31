"""RelativeVelocityTask — скорость одного тела относительно другого на прямой.

Положительное направление — вправо. Скорость A относительно B равна vA - vB.

Подтипы: относительная скорость и восстановление vA по относительной и vB.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class RelativeVelocityTask(BaseMathTask):
    TASK_TYPE = "relative_velocity"
    TASK_TYPES = ["relative", "first_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v": 6}, 2: {"v": 8}, 3: {"v": 10}, 4: {"v": 12}, 5: {"v": 12},
        6: {"v": 15}, 7: {"v": 18}, 8: {"v": 20}, 9: {"v": 24}, 10: {"v": 30},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        limit = int(p["v"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.va = random.randint(-limit, limit)
        self.vb = random.randint(-limit, limit)
        self.relative = self.va - self.vb
        self.answer = self.relative if self.task_type == "relative" else self.va
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "relative":
            ask = ((texts.t('s2', language, va=self.va, vb=self.vb)))
        else:
            ask = ((texts.t('s3', language, relative=self.relative, vb=self.vb)))
        return f"{rule} {ask}"

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        step = ((texts.t('s1', self.language, va=self.va, vb=self.vb, relative=self.relative)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
