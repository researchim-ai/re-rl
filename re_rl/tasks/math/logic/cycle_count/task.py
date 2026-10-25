"""CycleCountTask — циклы перестановки.

Образ каждого числа от 1 до n задан списком. Непройденное число открывает новый цикл.
Длина перестановки растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cycle_trace(perm: Sequence[int]) -> Tuple[List[Tuple[int, int, int]], List[int]]:
    size = len(perm) - 1
    seen = [0] * (size + 1)
    length_at = [0] * (size + 1)
    cycles = 0
    trace = []
    for start in range(1, size + 1):
        opened = 0
        if not seen[start]:
            opened = 1
            cycles += 1
            nodes = []
            point = start
            while not seen[point]:
                seen[point] = 1
                nodes.append(point)
                point = perm[point]
            for node in nodes:
                length_at[node] = len(nodes)
        trace.append((opened, cycles, length_at[start]))
    return trace, length_at


class CycleCountTask(BaseMathTask):
    TASK_TYPE = "cycle_count"
    TASK_TYPES = ["cycles", "length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        images = list(range(1, self.n + 1))
        random.shuffle(images)
        self.perm = [0] + images
        self.trace, self.length_at = cycle_trace(self.perm)
        self.cycles = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.length = self.length_at[self.k]
        self.answer = self.cycles if self.task_type == "cycles" else self.length
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        images = ", ".join(str(image) for image in self.perm[1:])
        key = "s0" if self.task_type == "cycles" else "s1"
        return texts.t(key, language, n=self.n, images=images, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, opened=opened, cycles=cycles, length=length)
            for index, (opened, cycles, length) in enumerate(self.trace, 1)
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
