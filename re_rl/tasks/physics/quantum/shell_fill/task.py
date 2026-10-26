"""ShellFillTask — заполнение подоболочек по Паули и Хунду.

Ёмкость чётная. Сначала по одному электрону на орбиталь, затем спаривание.
Число подоболочек растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def shell_trace(capacities: Sequence[int], electrons: int) -> List[Tuple[int, int]]:
    left = electrons
    placed = 0
    unpaired = 0
    trace = []
    for capacity in capacities:
        orbitals = capacity // 2
        take = min(left, capacity)
        left -= take
        singles = take if take <= orbitals else capacity - take
        placed += take
        unpaired += singles
        trace.append((placed, unpaired))
    return trace


class ShellFillTask(BaseMathTask):
    TASK_TYPE = "shell_fill"
    TASK_TYPES = ["placed", "unpaired"]
    CAPACITIES = (2, 6, 10)

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
        self.capacities = [random.choice(self.CAPACITIES) for _ in range(self.n)]
        total = sum(self.capacities)
        self.electrons = random.randint(0, total + 3)
        self.trace = shell_trace(self.capacities, self.electrons)
        self.placed = self.trace[-1][0]
        self.unpaired = self.trace[-1][1]
        self.answer = self.placed if self.task_type == "placed" else self.unpaired
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return " ".join(str(capacity) for capacity in self.capacities)

    def _descr(self, language):
        key = "s0" if self.task_type == "placed" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing(), electrons=self.electrons)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, placed=placed, unpaired=unpaired)
            for index, (placed, unpaired) in enumerate(self.trace, 1)
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
