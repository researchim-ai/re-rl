"""DragonFoldTask — последовательность поворотов кривой дракона.

Каждое сложение дописывает 1 и зеркально перевёрнутый хвост.
1 — поворот влево, 0 — вправо. Число сложений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def dragon_folds(folds: int) -> Tuple[List[int], List[Tuple[int, int]]]:
    turns = []
    stats = []
    for _ in range(folds):
        turns = turns + [1] + [1 - bit for bit in reversed(turns)]
        stats.append((sum(turns), len(turns)))
    return turns, stats


class DragonFoldTask(BaseMathTask):
    TASK_TYPE = "dragon_fold"
    TASK_TYPES = ["lefts", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 8}, 10: {"n": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.turns, self.stats = dragon_folds(self.n)
        self.lefts = self.stats[-1][0]
        self.k = random.randint(1, len(self.turns))
        self.at_k = self.turns[self.k - 1]
        self.answer = self.lefts if self.task_type == "lefts" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "lefts" else "s1"
        return texts.t(key, language, n=self.n, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, lefts=lefts, length=length)
            for index, (lefts, length) in enumerate(self.stats, 1)
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
