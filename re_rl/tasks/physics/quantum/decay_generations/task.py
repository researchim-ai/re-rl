"""DecayGenerationsTask — цепочка распада дискретными тиками.

За тик половина ядер каждого нестабильного вида переходит в следующий вид. Новые ядра в этот же тик не распадаются.
Последний вид стабилен. Число тиков растёт с уровнем, стартовое количество делится на 2 в этой степени.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def decay_tick(counts: List[int]) -> List[int]:
    species = len(counts)
    decayed = [counts[index] // 2 for index in range(species - 1)]
    updated = [0] * species
    for index in range(species - 1):
        updated[index] = counts[index] - decayed[index]
    updated[species - 1] = counts[species - 1]
    for index in range(species - 1):
        updated[index + 1] += decayed[index]
    return updated


class DecayGenerationsTask(BaseMathTask):
    TASK_TYPE = "decay_generations"
    TASK_TYPES = ["stable", "daughter"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "k": 3, "m": 2}, 2: {"n": 2, "k": 3, "m": 3},
        3: {"n": 3, "k": 3, "m": 3}, 4: {"n": 3, "k": 4, "m": 3},
        5: {"n": 4, "k": 4, "m": 4}, 6: {"n": 5, "k": 4, "m": 4},
        7: {"n": 6, "k": 5, "m": 4}, 8: {"n": 7, "k": 5, "m": 5},
        9: {"n": 8, "k": 5, "m": 5}, 10: {"n": 10, "k": 6, "m": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.species = max(3, int(p["k"]))
        self.seed_count = random.randint(1, int(p["m"]))
        self.history: List[List[int]] = []
        counts = [self.seed_count * 2 ** self.n] + [0] * (self.species - 1)
        for _ in range(self.n):
            counts = decay_tick(counts)
            self.history.append(counts)
        self.counts = counts
        self.stable = counts[-1]
        self.daughter = counts[1]
        self.answer = self.stable if self.task_type == "stable" else self.daughter
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "stable" else "s1"
        return texts.t(
            key, language, species=self.species, start=self.seed_count * 2 ** self.n,
            ticks=self.n,
        )

    def solve(self):
        steps = []
        for index, counts in enumerate(self.history, 1):
            shown = ", ".join(str(item) for item in counts)
            steps.append(texts.t("s2", self.language, i=index, counts=shown))
        steps.append(texts.t(
            "s3", self.language, stable=self.stable, daughter=self.daughter, source=self.counts[0],
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
