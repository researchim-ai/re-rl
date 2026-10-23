"""SaturateCountTask — счётчик с потолком и сбросом.

Единица прибавляет один, пока значение ниже потолка. На потолке лишняя единица только считается.
Ноль сбрасывает значение. Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def saturate_trace(ops: Sequence[int], cap: int) -> List[Tuple[int, int]]:
    value = 0
    hits = 0
    trace = []
    for op in ops:
        if op == 0:
            value = 0
        elif value == cap:
            hits += 1
        else:
            value += 1
        trace.append((value, hits))
    return trace


class SaturateCountTask(BaseMathTask):
    TASK_TYPE = "saturate_count"
    TASK_TYPES = ["value", "hits"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "cap": 2}, 2: {"n": 4, "cap": 2}, 3: {"n": 5, "cap": 3},
        4: {"n": 6, "cap": 3}, 5: {"n": 8, "cap": 4}, 6: {"n": 9, "cap": 4},
        7: {"n": 10, "cap": 5}, 8: {"n": 12, "cap": 5}, 9: {"n": 14, "cap": 6},
        10: {"n": 16, "cap": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.cap = max(1, int(p["cap"]))
        self.ops = [random.choice((0, 1, 1, 1)) for _ in range(self.n)]
        self.trace = saturate_trace(self.ops, self.cap)
        self.value, self.hits = self.trace[-1]
        self.answer = self.value if self.task_type == "value" else self.hits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(op) for op in self.ops)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, cap=self.cap, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, op=op, value=value, hits=hits)
            for index, (op, (value, hits)) in enumerate(zip(self.ops, self.trace), 1)
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
