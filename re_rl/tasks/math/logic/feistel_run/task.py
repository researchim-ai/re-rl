"""FeistelRunTask — раунды сети Фейстеля.

Новая левая половина равна старой правой. Новая правая равна старой левой, сложенной побитово по модулю 2 с суммой правой половины и ключа.
Число раундов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

HALF = 16


def feistel_trace(left: int, right: int, keys: Sequence[int]) -> List[Tuple[int, int]]:
    trace = []
    for item in keys:
        mixed = (right + item) % HALF
        left, right = right, left ^ mixed
        trace.append((left, right))
    return trace


class FeistelRunTask(BaseMathTask):
    TASK_TYPE = "feistel_run"
    TASK_TYPES = ["left", "pack"]
    HALF = HALF

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
        self.left = random.randrange(self.HALF)
        self.right = random.randrange(self.HALF)
        self.keys = [random.randrange(self.HALF) for _ in range(self.n)]
        self.trace = feistel_trace(self.left, self.right, self.keys)
        self.final_left = self.trace[-1][0]
        self.pack = self.final_left * self.HALF + self.trace[-1][1]
        self.answer = self.final_left if self.task_type == "left" else self.pack
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        keys = ", ".join(str(item) for item in self.keys)
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(key, language, n=self.n, left=self.left, right=self.right,
                       keys=keys, half=self.HALF)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, item=item, left=left, right=right)
            for index, (item, (left, right)) in enumerate(zip(self.keys, self.trace), 1)
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
