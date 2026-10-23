"""CrtLiftTask — поиск общего остатка для двух соседних модулей.

Модули идут подряд, поэтому они взаимно просты. Перебираются кратные первого модуля.
Число проб равно второму модулю и растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def crt_search(remain_a: int, mod_a: int, remain_b: int, mod_b: int) -> List[Tuple[int, int, int]]:
    trace = []
    for lift in range(mod_b):
        value = remain_a + mod_a * lift
        residue = value % mod_b
        trace.append((value, residue, 1 if residue == remain_b else 0))
    return trace


class CrtLiftTask(BaseMathTask):
    TASK_TYPE = "crt_lift"
    TASK_TYPES = ["value", "lift"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6},
        5: {"n": 7}, 6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.mod_b = self.n
        self.mod_a = self.n - 1
        self.remain_a = random.randint(0, self.mod_a - 1)
        self.remain_b = random.randint(0, self.mod_b - 1)
        self.trace = crt_search(self.remain_a, self.mod_a, self.remain_b, self.mod_b)
        self.lift = next(index for index, row in enumerate(self.trace) if row[2])
        self.value = self.trace[self.lift][0]
        self.answer = self.value if self.task_type == "value" else self.lift
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(
            key, language, a=self.remain_a, m=self.mod_a, b=self.remain_b, n=self.mod_b,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, t=index, value=value, residue=residue, hit=hit)
            for index, (value, residue, hit) in enumerate(self.trace)
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
