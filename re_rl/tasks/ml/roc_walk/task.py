"""RocWalkTask — проход по оценкам от больших к меньшим.

При равной оценке раньше идёт левый объект. Положительный класс — 1.
Число объектов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def roc_trace(pairs: Sequence[Pair]) -> List[Tuple[int, int, int, int]]:
    order = sorted(range(len(pairs)), key=lambda index: (-pairs[index][0], index))
    hits = 0
    traps = 0
    trace = []
    for index in order:
        score, label = pairs[index]
        if label:
            hits += 1
        else:
            traps += 1
        trace.append((score, label, hits, traps))
    return trace


class RocWalkTask(BaseMathTask):
    TASK_TYPE = "roc_walk"
    TASK_TYPES = ["top", "traps"]

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
        self.pairs = [
            (random.randint(0, 9), random.randint(0, 1))
            for _ in range(self.n)
        ]
        self.pairs[0] = (self.pairs[0][0], 1)
        self.trace = roc_trace(self.pairs)
        self.top = next((index for index, row in enumerate(self.trace, 1) if row[1] == 1), 0)
        self.traps = self.top - 1 if self.top else self.n
        self.answer = self.top if self.task_type == "top" else self.traps
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{score}, {label}" for score, label in self.pairs)
        key = "s0" if self.task_type == "top" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, score=score, label=label, hits=hits, traps=traps)
            for index, (score, label, hits, traps) in enumerate(self.trace, 1)
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
