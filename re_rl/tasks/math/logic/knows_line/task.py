"""KnowsLineTask — знание на цепочке неразличимых миров.

Открытая дверь сливает соседние миры в один класс, и слияние транзитивно.
Агент знает атом, если тот истинен во всём классе.
Число миров растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def knows_trace(bits: Sequence[int], doors: Sequence[int]) -> List[Tuple[int, int]]:
    size = len(bits)
    segment = [0] * size
    current = 0
    for index in range(size - 1):
        segment[index] = current
        if not doors[index]:
            current += 1
    if size:
        segment[size - 1] = current
    pure = {}
    for index, bit in enumerate(bits):
        mark = segment[index]
        if mark not in pure:
            pure[mark] = 1
        if bit == 0:
            pure[mark] = 0
    known = 0
    trace = []
    for mark in segment:
        holds = pure[mark]
        known += holds
        trace.append((holds, known))
    return trace


class KnowsLineTask(BaseMathTask):
    TASK_TYPE = "knows_line"
    TASK_TYPES = ["known", "here"]

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
        self.bits = [random.randint(0, 1) for _ in range(self.n)]
        self.doors = [random.randint(0, 1) for _ in range(self.n - 1)]
        self.trace = knows_trace(self.bits, self.doors)
        self.known = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.trace[self.k - 1][0]
        self.answer = self.known if self.task_type == "known" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        bits = ", ".join(str(bit) for bit in self.bits)
        doors = ", ".join(str(door) for door in self.doors)
        key = "s0" if self.task_type == "known" else "s1"
        return texts.t(key, language, n=self.n, bits=bits, doors=doors, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, holds=holds, known=known)
            for index, (holds, known) in enumerate(self.trace, 1)
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
