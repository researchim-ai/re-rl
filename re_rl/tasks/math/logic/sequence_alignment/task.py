"""SequenceAlignmentTask — вес глобального выравнивания Нидлмана–Вунша.

Совпадение даёт +1, несовпадение и дырка дают -1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ALPHABET = "acgt"


def alignment_score(left: str, right: str, match: int = 1, mismatch: int = -1, gap: int = -1) -> int:
    n, m = len(left), len(right)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = i * gap
    for j in range(1, m + 1):
        dp[0][j] = j * gap
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diagonal = dp[i - 1][j - 1] + (match if left[i - 1] == right[j - 1] else mismatch)
            dp[i][j] = max(diagonal, dp[i - 1][j] + gap, dp[i][j - 1] + gap)
    return dp[n][m]


class SequenceAlignmentTask(BaseMathTask):
    TASK_TYPE = "sequence_alignment"
    TASK_TYPES = ["score"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 4}, 3: {"n": 4}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["n"])
        self.task_type = "score"
        self.augment = augment
        self.left = "".join(random.choice(_ALPHABET) for _ in range(self.length))
        self.right = "".join(random.choice(_ALPHABET) for _ in range(random.randint(2, self.length)))
        self.answer = alignment_score(self.left, self.right)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, left=self.left, right=self.right)))

    def solve(self):
        step = ((texts.t('s1', self.language, answer=self.answer)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=self.answer)))]
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
