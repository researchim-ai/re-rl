"""ParitySheetTask — чётность строк из битов.

Чётность строки — остаток суммы битов при делении на 2.
Число строк растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def parity_trace(rows: Sequence[Sequence[int]]) -> List[Tuple[int, int]]:
    odds = 0
    trace = []
    for row in rows:
        bit = sum(row) % 2
        odds += bit
        trace.append((bit, odds))
    return trace


class ParitySheetTask(BaseMathTask):
    TASK_TYPE = "parity_sheet"
    TASK_TYPES = ["odds", "bit"]

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
        self.rows = [[random.randint(0, 1) for _ in range(4)] for _ in range(self.n)]
        self.trace = parity_trace(self.rows)
        self.odds = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.bit = self.trace[self.k - 1][0]
        self.answer = self.odds if self.task_type == "odds" else self.bit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rows = " | ".join(" ".join(str(bit) for bit in row) for row in self.rows)
        key = "s0" if self.task_type == "odds" else "s1"
        return texts.t(key, language, n=self.n, rows=rows, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, bit=bit, odds=odds)
            for index, (bit, odds) in enumerate(self.trace, 1)
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
