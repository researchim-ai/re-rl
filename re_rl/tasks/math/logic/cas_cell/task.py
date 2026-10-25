"""CasCellTask — запись в ячейку только при совпадении версии.

Чужая версия оставляет и значение, и версию на месте.
Число попыток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Attempt = Tuple[int, int]


def cas_trace(attempts: Sequence[Attempt]) -> List[Tuple[int, int, int]]:
    value = 0
    version = 0
    writes = 0
    trace = []
    for expect, new in attempts:
        if expect == version:
            value = new
            version += 1
            writes += 1
        trace.append((value, version, writes))
    return trace


class CasCellTask(BaseMathTask):
    TASK_TYPE = "cas_cell"
    TASK_TYPES = ["writes", "value"]

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
        self.attempts = []
        version = 0
        for _ in range(self.n):
            expect = version if random.randrange(3) else random.randint(0, self.n)
            new = random.randint(0, 9)
            self.attempts.append((expect, new))
            if expect == version:
                version += 1
        self.trace = cas_trace(self.attempts)
        self.final_value = self.trace[-1][0]
        self.writes = self.trace[-1][2]
        self.answer = self.writes if self.task_type == "writes" else self.final_value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{expect} {new}" for expect, new in self.attempts)
        key = "s0" if self.task_type == "writes" else "s1"
        return texts.t(key, language, n=self.n, attempts=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, expect=expect, new=new, value=value, version=version, writes=writes)
            for index, ((expect, new), (value, version, writes)) in enumerate(zip(self.attempts, self.trace), 1)
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
