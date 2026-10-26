"""FranckHertzTask — неупругие столкновения с фиксированным квантом.

Если энергии хватает, она уменьшается на один квант. Иначе столкновение упругое.
Число столкновений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hertz_trace(energy: int, quantum: int, hits: int) -> List[Tuple[int, int]]:
    left = energy
    drops = 0
    trace = []
    for _ in range(hits):
        if left >= quantum:
            left -= quantum
            drops += 1
        trace.append((left, drops))
    return trace


class FranckHertzTask(BaseMathTask):
    TASK_TYPE = "franck_hertz"
    TASK_TYPES = ["left", "drops"]

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
        self.quantum = random.randint(2, 6)
        self.energy = random.randint(0, self.quantum * self.n + 5)
        self.trace = hertz_trace(self.energy, self.quantum, self.n)
        self.left = self.trace[-1][0]
        self.drops = self.trace[-1][1]
        self.answer = self.left if self.task_type == "left" else self.drops
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "left" else "s1"
        return texts.t(key, language, n=self.n, energy=self.energy, quantum=self.quantum)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, drops=drops)
            for index, (left, drops) in enumerate(self.trace, 1)
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
