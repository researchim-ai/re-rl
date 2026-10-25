"""ShortCircuitTask — короткое замыкание конъюнкции и дизъюнкции.

И не читает правый бит, если слева уже 0. Или не читает правый бит, если слева уже 1.
Число операндов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def short_trace(start: int, steps: Sequence[Step]) -> List[Tuple[int, int]]:
    value = start
    reads = 1
    trace = [(value, reads)]
    for op, bit in steps:
        if (value == 0 and op == 0) or (value == 1 and op == 1):
            trace.append((value, reads))
            continue
        reads += 1
        value = value & bit if op == 0 else value | bit
        trace.append((value, reads))
    return trace


class ShortCircuitTask(BaseMathTask):
    TASK_TYPE = "short_circuit"
    TASK_TYPES = ["value", "reads"]

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
        self.start = random.randint(0, 1)
        self.steps = [(random.randint(0, 1), random.randint(0, 1)) for _ in range(self.n - 1)]
        self.trace = short_trace(self.start, self.steps)
        self.value = self.trace[-1][0]
        self.reads = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.reads
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{op} {bit}" for op, bit in self.steps)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, steps=shown)

    def solve(self):
        steps = [texts.t("s2", self.language, i=1, op=0, bit=self.start, value=self.trace[0][0], reads=self.trace[0][1])]
        for index, ((op, bit), (value, reads)) in enumerate(zip(self.steps, self.trace[1:]), 2):
            steps.append(texts.t("s3", self.language, i=index, op=op, bit=bit, value=value, reads=reads))
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
