"""PermConjTask — сопряжение подстановок.

Сопряжённая переводит сигма(x) в сигма(тау(x)). Число неподвижных точек сохраняется.
Степень подстановок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _inverse(images: Sequence[int]) -> List[int]:
    inverse = [0] * len(images)
    for index, image in enumerate(images):
        inverse[image - 1] = index + 1
    return inverse


def conj_trace(sigma: Sequence[int], tau: Sequence[int]) -> List[Tuple[int, int]]:
    inverse = _inverse(sigma)
    fixed = 0
    trace = []
    for point in range(1, len(sigma) + 1):
        preimage = inverse[point - 1]
        moved = tau[preimage - 1]
        image = sigma[moved - 1]
        if image == point:
            fixed += 1
        trace.append((image, fixed))
    tau_fixed = sum(1 for index, image in enumerate(tau, 1) if image == index)
    if fixed != tau_fixed:
        raise RuntimeError("fixed mismatch")
    return trace


class PermConjTask(BaseMathTask):
    TASK_TYPE = "perm_conj"
    TASK_TYPES = ["image", "fixed"]

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
        self.sigma = list(range(1, self.n + 1))
        self.tau = list(range(1, self.n + 1))
        random.shuffle(self.sigma)
        random.shuffle(self.tau)
        self.k = random.randint(1, self.n)
        self.trace = conj_trace(self.sigma, self.tau)
        self.image = self.trace[self.k - 1][0]
        self.fixed = self.trace[-1][1]
        self.answer = self.image if self.task_type == "image" else self.fixed
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _row(self, images: Sequence[int]) -> str:
        return " ".join(str(image) for image in images)

    def _descr(self, language):
        key = "s0" if self.task_type == "image" else "s1"
        return texts.t(
            key, language, n=self.n, sigma=self._row(self.sigma),
            tau=self._row(self.tau), k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, image=image, fixed=fixed)
            for index, (image, fixed) in enumerate(self.trace, 1)
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
