"""CellPatchTask — журнал записей в массив и число настоящих изменений.

Запись, которая ставит уже лежащее значение, не считается изменением.
Число записей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Edit = Tuple[int, int]


def patch_trace(size: int, edits: Sequence[Edit]) -> List[Tuple[int, int]]:
    cells = [0] * (size + 1)
    changed = 0
    trace = []
    for index, value in edits:
        if cells[index] != value:
            cells[index] = value
            changed += 1
        trace.append((changed, cells[index]))
    return trace, cells


class CellPatchTask(BaseMathTask):
    TASK_TYPE = "cell_patch"
    TASK_TYPES = ["cell", "writes"]

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
        self.edits = [
            (random.randint(1, self.n), random.randint(0, 6))
            for _ in range(self.n)
        ]
        self.trace, self.cells = patch_trace(self.n, self.edits)
        self.writes = self.trace[-1][0]
        self.k = random.randint(1, self.n)
        self.cell = self.cells[self.k]
        self.answer = self.cell if self.task_type == "cell" else self.writes
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{index}={value}" for index, value in self.edits)
        key = "s0" if self.task_type == "cell" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=step, index=index, value=value, writes=writes)
            for step, ((index, value), (writes, _)) in enumerate(zip(self.edits, self.trace), 1)
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
