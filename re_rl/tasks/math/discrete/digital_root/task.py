"""DigitalRootTask — цифровой корень и число сложений цифр.

Корень числа n ≥ 1 равен 1 + (n − 1) mod 9. Число шагов считается явно.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def digit_chain(n: int) -> Tuple[str, int, int]:
    parts = [str(n)]
    steps = 0
    while n >= 10:
        n = sum(int(ch) for ch in str(n))
        parts.append(str(n))
        steps += 1
    return " → ".join(parts), n, steps


class DigitalRootTask(BaseMathTask):
    TASK_TYPE = "digital_root"
    TASK_TYPES = ["root", "steps"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 40}, 2: {"n": 80}, 3: {"n": 200}, 4: {"n": 500}, 5: {"n": 1000},
        6: {"n": 5000}, 7: {"n": 20000}, 8: {"n": 100000}, 9: {"n": 500000}, 10: {"n": 2000000},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = random.randint(1, int(p["n"]))
        self.chain, self.root, self.steps = digit_chain(self.n)
        self.answer = self.root if self.task_type == "root" else self.steps
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "root" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        step = texts.t("s2", self.language, chain=self.chain, root=self.root, steps=self.steps)
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
