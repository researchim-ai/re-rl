"""ParallaxTask — годичный параллакс.

Расстояние в парсеках d = 1 / p, где p — параллакс в угловых секундах.
Ответ — точная дробь или целое.

Подтипы: ``distance`` (даны секунды дуги) и ``parallax`` (даны парсеки).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


class ParallaxTask(BaseMathTask):
    TASK_TYPE = "stellar_parallax"
    TASK_TYPES = ["distance", "parallax"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"d": 5}, 2: {"d": 8}, 3: {"d": 10}, 4: {"d": 12}, 5: {"d": 15},
        6: {"d": 20}, 7: {"d": 24}, 8: {"d": 30}, 9: {"d": 40}, 10: {"d": 50},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        # p = num/den угловых секунд, d = den/num парсек.
        self.num = 1 if difficulty < 6 else random.choice([1, 1, 2, 3])
        self.den = random.randint(1, int(p["d"]))
        if self.num > 1 and self.den % self.num == 0:
            self.den += 1
        self.parallax = Fraction(self.num, self.den)
        self.distance = Fraction(self.den, self.num)
        self.answer = self.distance if self.task_type == "distance" else self.parallax
        if self.parallax * self.distance != 1:
            raise RuntimeError(texts.t('s4', language))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        if self.task_type == "distance":
            ask = ((texts.t('s2', language, v0=fmt_fraction(self.parallax))))
        else:
            ask = ((texts.t('s3', language, v0=fmt_fraction(self.distance))))
        return f"{rule} {ask}"

    def solve(self):
        shown = fmt_fraction(self.answer)
        step = ((texts.t('s1', self.language, v0=fmt_fraction(self.distance), v1=fmt_fraction(self.parallax))))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=shown)))]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
