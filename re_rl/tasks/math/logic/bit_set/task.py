"""BitSetTask — установка и снятие отдельных битов.

Биты нумеруются от 0 до 3. Установка уже поднятого бита новым включением не считается.
Число команд растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Op = Tuple[int, int]


def bitset_trace(ops: Sequence[Op]) -> List[Tuple[int, int]]:
    mask = 0
    news = 0
    trace = []
    for kind, bit in ops:
        flag = 1 << bit
        if kind == 1:
            if mask & flag == 0:
                news += 1
            mask |= flag
        else:
            mask &= ~flag
        trace.append((mask, news))
    return trace


class BitSetTask(BaseMathTask):
    TASK_TYPE = "bit_set"
    TASK_TYPES = ["mask", "news"]

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
        self.ops = [(random.randint(0, 1), random.randint(0, 3)) for _ in range(self.n)]
        self.trace = bitset_trace(self.ops)
        self.mask = self.trace[-1][0]
        self.news = self.trace[-1][1]
        self.answer = self.mask if self.task_type == "mask" else self.news
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{kind} {bit}" for kind, bit in self.ops)
        key = "s0" if self.task_type == "mask" else "s1"
        return texts.t(key, language, n=self.n, ops=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, kind=kind, bit=bit, mask=mask, news=news)
            for index, ((kind, bit), (mask, news)) in enumerate(zip(self.ops, self.trace), 1)
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
