"""HashProbeTask — вставка с линейным пробированием.

Место — остаток от деления ключа на размер таблицы. Занятая клетка сдвигает поиск на одну вперёд по кругу.
Размер таблицы равен числу ключей и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def probe_trace(size: int, keys: Sequence[int]) -> List[Tuple[int, int]]:
    table = [-1] * size
    total = 0
    trace = []
    for key in keys:
        slot = key % size
        probes = 1
        while table[slot] != -1:
            slot = (slot + 1) % size
            probes += 1
        table[slot] = key
        total += probes
        trace.append((slot, total))
    return trace


class HashProbeTask(BaseMathTask):
    TASK_TYPE = "hash_probe"
    TASK_TYPES = ["slot", "probes"]

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
        self.keys = [random.randint(0, self.n * 3) for _ in range(self.n)]
        self.trace = probe_trace(self.n, self.keys)
        self.slot = self.trace[-1][0]
        self.probes = self.trace[-1][1]
        self.answer = self.slot if self.task_type == "slot" else self.probes
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(key) for key in self.keys)
        key = "s0" if self.task_type == "slot" else "s1"
        return texts.t(key, language, n=self.n, keys=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, item=item, slot=slot, probes=probes)
            for index, (item, (slot, probes)) in enumerate(zip(self.keys, self.trace), 1)
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
