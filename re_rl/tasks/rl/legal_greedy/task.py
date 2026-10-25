"""LegalGreedyTask — жадный выбор среди разрешённых действий.

У действия маска 1, если оно разрешено. Среди разрешённых берётся большая оценка, при равенстве меньший номер.
Число состояний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int, int, int]


def legal_trace(rows: Sequence[Row]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for q0, q1, allow0, allow1 in rows:
        if allow0 and (not allow1 or q0 >= q1):
            choice = 0
        else:
            choice = 1
        total += choice
        trace.append((choice, total))
    return trace


class LegalGreedyTask(BaseMathTask):
    TASK_TYPE = "legal_greedy"
    TASK_TYPES = ["total", "last"]

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
        self.rows: List[Row] = []
        for _ in range(self.n):
            allow0 = random.randint(0, 1)
            allow1 = random.randint(0, 1)
            if allow0 == 0 and allow1 == 0:
                allow0 = 1
            self.rows.append((random.randint(-3, 5), random.randint(-3, 5), allow0, allow1))
        self.trace = legal_trace(self.rows)
        self.total = self.trace[-1][1]
        self.last = self.trace[-1][0]
        self.answer = self.total if self.task_type == "total" else self.last
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{q0} {q1} {allow0} {allow1}" for q0, q1, allow0, allow1 in self.rows)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, rows=shown)

    def solve(self):
        steps = []
        for index, ((q0, q1, allow0, allow1), (choice, total)) in enumerate(zip(self.rows, self.trace), 1):
            steps.append(texts.t(
                "s2", self.language, i=index, q0=q0, q1=q1, a0=allow0, a1=allow1,
                choice=choice, total=total,
            ))
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
