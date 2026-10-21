"""CatalanTask — числа Каталана.

C(0) = 1, C(n+1) = C(n) * (4n + 2) / (n + 2). Деление всегда нацело.

Подтипы:
- ``number``     — само число C(n);
- ``parentheses``— сколько правильных скобочных последовательностей из n пар (тоже C(n)).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def catalan_sequence(n: int) -> List[int]:
    seq = [1]
    c = 1
    for k in range(n):
        nxt = c * (4 * k + 2)
        if nxt % (k + 2) != 0:
            raise RuntimeError(texts.literal('literals.s6'))
        c = nxt // (k + 2)
        seq.append(c)
    return seq


class CatalanTask(BaseMathTask):
    TASK_TYPE = "catalan"
    TASK_TYPES = ["number", "parentheses"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 6},
        6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9}, 9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.seq = catalan_sequence(self.n)
        self.answer = self.seq[-1]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        if self.task_type == "number":
            return ((texts.t('s1', language, n=self.n)))
        return ((texts.t('s0', language, n=self.n)))

    def solve(self):
        shown = ", ".join(f"C({i})={v}" for i, v in enumerate(self.seq))
        note = (texts.t('s2', self.language) if self.task_type == "parentheses" else texts.t('s3', self.language))
        note_en = (texts.t('s4', self.language) if self.task_type == "parentheses" else texts.t('s5', self.language))
        self.solution_steps = [
            ((f"{note} {shown}.")),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
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
