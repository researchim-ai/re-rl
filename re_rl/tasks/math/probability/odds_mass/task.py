"""OddsMassTask — целые веса двух гипотез после свидетельств.

Каждое свидетельство умножает вес своей гипотезы. Итог — несокращённые произведения.
Число свидетельств растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def odds_trace(favor: int, against: int, pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    trace = []
    for yes, no in pairs:
        favor *= yes
        against *= no
        trace.append((favor, favor + against))
    return trace


class OddsMassTask(BaseMathTask):
    TASK_TYPE = "odds_mass"
    TASK_TYPES = ["favor", "total"]

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
        self.favor = random.randint(1, 4)
        self.against = random.randint(1, 4)
        self.pairs = [(random.randint(1, 3), random.randint(1, 3)) for _ in range(self.n)]
        self.trace = odds_trace(self.favor, self.against, self.pairs)
        self.final_favor = self.trace[-1][0]
        self.total = self.trace[-1][1]
        self.answer = self.final_favor if self.task_type == "favor" else self.total
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{yes} {no}" for yes, no in self.pairs)
        key = "s0" if self.task_type == "favor" else "s1"
        return texts.t(
            key, language, n=self.n, favor=self.favor, against=self.against, pairs=shown,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, yes=yes, no=no, favor=favor, total=total)
            for index, ((yes, no), (favor, total)) in enumerate(zip(self.pairs, self.trace), 1)
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
