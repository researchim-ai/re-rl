"""SetReasoningTask — задачи на множества и принцип включения-исключения.

Подтипы (2 множества):
- union: |A ∪ B|;
- only_a: сколько только в A (не в B);
- neither: сколько ни в A, ни в B (нужен размер универсума).
Данные генерируются согласованно, ответ вычисляется точно.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class SetReasoningTask(BaseMathTask):
    TASK_TYPE = "set_reasoning"
    TASK_TYPES = ["union", "only_a", "neither"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max": 20}, 2: {"max": 30}, 3: {"max": 40}, 4: {"max": 60}, 5: {"max": 80},
        6: {"max": 100}, 7: {"max": 150}, 8: {"max": 200}, 9: {"max": 300}, 10: {"max": 500},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.max = int(preset["max"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        # Разбиваем универсум на 4 непересекающиеся области.
        both = random.randint(1, max(1, self.max // 5))
        only_a = random.randint(1, max(1, self.max // 4))
        only_b = random.randint(1, max(1, self.max // 4))
        neither = random.randint(0, max(1, self.max // 5))
        self.total = both + only_a + only_b + neither
        self.A = only_a + both
        self.B = only_b + both
        self.both = both
        self.only_a = only_a
        self.only_b = only_b
        self.neither = neither
        self.union = only_a + only_b + both

        if self.subtype == "union":
            self._answer = self.union
        elif self.subtype == "only_a":
            self._answer = self.only_a
        else:
            self._answer = self.neither

    def _make_description(self, language: str) -> str:
        base = ((texts.t('s0', language, total=self.total, A=self.A, B=self.B, both=self.both)))
        if self.subtype == "union":
            q = ((texts.t('s1', language)))
        elif self.subtype == "only_a":
            q = ((texts.t('s3', language)))
        else:
            q = ((texts.t('s4', language)))
        return base + q

    def solve(self):
        if self.subtype == "union":
            step = ((f"|A ∪ B| = |A| + |B| − |A ∩ B| = {self.A} + {self.B} − {self.both} = {self._answer}."))
        elif self.subtype == "only_a":
            step = ((texts.t('s5', self.language, A=self.A, both=self.both, _answer=self._answer)))
        else:
            step = ((texts.t('s6', self.language, total=self.total, union=self.union, _answer=self._answer)))
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            step,
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
