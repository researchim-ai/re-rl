"""RefResolveTask — раскрытие ссылок на уже заполненные ячейки.

Ссылка только назад. Номер вне уже заполненных ячеек даёт ноль и копией не считается.
Число ячеек растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Cell = Tuple[int, int]


def deref_trace(cells: Sequence[Cell]) -> List[Tuple[int, int]]:
    values = []
    copies = 0
    trace = []
    for kind, arg in cells:
        if kind == 0:
            value = arg
        elif 0 <= arg < len(values):
            value = values[arg]
            copies += 1
        else:
            value = 0
        values.append(value)
        trace.append((value, copies))
    return trace


class RefResolveTask(BaseMathTask):
    TASK_TYPE = "ref_resolve"
    TASK_TYPES = ["last", "copies"]

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
        self.cells = []
        for index in range(self.n):
            if index == 0 or random.randrange(2) == 0:
                self.cells.append((0, random.randint(0, 9)))
            elif random.randrange(4) == 0:
                self.cells.append((1, random.randint(index, index + 2)))
            else:
                self.cells.append((1, random.randrange(index)))
        self.trace = deref_trace(self.cells)
        self.last = self.trace[-1][0]
        self.copies = self.trace[-1][1]
        self.answer = self.last if self.task_type == "last" else self.copies
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{kind} {arg}" for kind, arg in self.cells)
        key = "s0" if self.task_type == "last" else "s1"
        return texts.t(key, language, n=self.n, cells=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, code=kind, arg=arg, value=value, copies=copies)
            for index, ((kind, arg), (value, copies)) in enumerate(zip(self.cells, self.trace), 1)
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
