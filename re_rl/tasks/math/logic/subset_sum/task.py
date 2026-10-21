"""Задачи комбинаторной оптимизации: рюкзак 0/1 и сумма подмножества."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, List
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

class SubsetSumTask(BaseMathTask):
    TASK_TYPE = "subset_sum"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "vmax": 9}, 2: {"n": 5, "vmax": 12}, 3: {"n": 5, "vmax": 15},
        4: {"n": 6, "vmax": 15}, 5: {"n": 7, "vmax": 20}, 6: {"n": 8, "vmax": 20},
        7: {"n": 9, "vmax": 25}, 8: {"n": 10, "vmax": 30}, 9: {"n": 11, "vmax": 35},
        10: {"n": 12, "vmax": 40},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.vmax = int(p["n"]), int(p["vmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.nums = [random.randint(1, self.vmax) for _ in range(self.n)]
        if random.random() < 0.5:  # заведомо достижимая цель
            k = random.randint(1, self.n)
            self.target = sum(random.sample(self.nums, k))
        else:
            self.target = random.randint(1, sum(self.nums))
        self._answer = self._reachable()

    def _reachable(self):
        possible = {0}
        for x in self.nums:
            possible |= {p + x for p in possible}
        return self.target in possible

    def _descr(self, language):
        return ((texts.t('s0', language, v0=', '.join(map(str, self.nums)), target=self.target)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language) if self._answer else texts.t('s5', self.language))),
        ]
        self.final_answer = (texts.t('s1', self.language) if self._answer else texts.t('s2', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
