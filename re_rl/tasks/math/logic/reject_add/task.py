"""RejectAddTask — прибавление отклоняется целиком, если выходит за пределы.

Отклонённое прибавление не меняет значение. Принятое записывается полностью.
Число прибавлений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def reject_trace(start: int, limit: int, adds: Sequence[int]) -> List[Tuple[int, int]]:
    value = start
    rejects = 0
    trace = []
    for add in adds:
        nxt = value + add
        if 0 <= nxt <= limit:
            value = nxt
        else:
            rejects += 1
        trace.append((value, rejects))
    return trace


class RejectAddTask(BaseMathTask):
    TASK_TYPE = "reject_add"
    TASK_TYPES = ["rejects", "value"]

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
        self.limit = self.n
        self.start = random.randint(0, self.limit)
        self.adds = [random.randint(-self.limit, self.limit) for _ in range(self.n)]
        self.trace = reject_trace(self.start, self.limit, self.adds)
        self.final_value = self.trace[-1][0]
        self.rejects = self.trace[-1][1]
        self.answer = self.rejects if self.task_type == "rejects" else self.final_value
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(add) for add in self.adds)
        key = "s0" if self.task_type == "rejects" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, limit=self.limit, adds=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, add=add, value=value, rejects=rejects)
            for index, (add, (value, rejects)) in enumerate(zip(self.adds, self.trace), 1)
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
