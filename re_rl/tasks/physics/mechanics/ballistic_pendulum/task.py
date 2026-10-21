"""BallisticPendulumTask — баллистический маятник.

Неупругий удар: m v = (m + M) V.
Дальше подъём: V^2 = 2 g h, g = 10 м/с^2.

Числа подобраны так, что V и h целые: V кратно 10, тогда h = V^2 / 20 — целое,
а отношение (m + M) / m — целое, поэтому скорость пули тоже целая.
Массы заданы в граммах; в законе сохранения импульса важны только их отношения.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class BallisticPendulumTask(BaseMathTask):
    TASK_TYPE = "ballistic_pendulum"
    TASK_TYPES = ["block_speed", "height", "bullet_speed"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"s": 3, "a": 1}, 2: {"s": 4, "a": 1}, 3: {"s": 5, "a": 2},
        4: {"s": 5, "a": 2}, 5: {"s": 6, "a": 2}, 6: {"s": 8, "a": 3},
        7: {"s": 8, "a": 3}, 8: {"s": 10, "a": 3}, 9: {"s": 10, "a": 4},
        10: {"s": 12, "a": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.s_max = int(p["s"])
        self.a_max = int(p["a"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # (m+M)/m = s >= 2, массы в граммах.
        self.s = random.randint(2, max(2, self.s_max))
        self.m = random.choice([10, 20, 25, 50])
        self.M = self.m * (self.s - 1)
        self.a = random.randint(1, max(1, self.a_max))
        self.V = 10 * self.a
        self.h = 5 * self.a * self.a  # V^2 / (2*10)
        self.v = self.V * self.s
        if self.m * self.v != self.V * (self.m + self.M):
            raise RuntimeError(texts.t('s7', self.language))
        if self.V * self.V != 20 * self.h:
            raise RuntimeError(texts.t('s8', self.language))
        self.answer = {"block_speed": self.V, "height": self.h, "bullet_speed": self.v}[self.task_type]

    def _descr(self, language):
        g = ((texts.t('s0', language)))
        common = ((texts.t('s1', language, m=self.m, M=self.M)))
        if self.task_type == "block_speed":
            ask = ((texts.t('s4', language, v=self.v)))
        elif self.task_type == "height":
            ask = ((texts.t('s5', language, v=self.v)))
        else:
            ask = ((texts.t('s6', language, h=self.h)))
        return f"{common} {g} {ask}"

    def solve(self):
        momentum = ((texts.t('s2', self.language, m=self.m, v=self.v, m_2=self.m, M=self.M, V=self.V)))
        energy = ((texts.t('s3', self.language, V=self.V, h=self.h)))
        if self.task_type == "block_speed":
            steps = [momentum]
        elif self.task_type == "height":
            steps = [momentum, energy]
        else:
            steps = [energy, momentum]
        steps.append((texts.common('answer_line', self.language, answer=self.answer)))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
