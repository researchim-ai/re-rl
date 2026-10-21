"""Классические задачи динамического программирования на подпоследовательностях.

Подтипы:
- ``lis`` — длина наибольшей строго возрастающей подпоследовательности;
- ``lps`` — длина наибольшей палиндромной подпоследовательности строки.

Масштаб задаётся длиной последовательности/строки.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import string
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U


class LISDPTask(BaseMathTask):
    TASK_TYPE = "lis_dp"
    TASK_TYPES = ["lis", "lps"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "alpha": 4}, 2: {"n": 6, "alpha": 4}, 3: {"n": 7, "alpha": 5},
        4: {"n": 8, "alpha": 5}, 5: {"n": 10, "alpha": 6}, 6: {"n": 12, "alpha": 6},
        7: {"n": 14, "alpha": 7}, 8: {"n": 16, "alpha": 7}, 9: {"n": 18, "alpha": 8},
        10: {"n": 20, "alpha": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n, self.alpha = int(p["n"]), int(p["alpha"])
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.task_type == "lis":
            self.seq = [random.randint(1, self.n) for _ in range(self.n)]
            self.answer = self._lis(self.seq)
        else:
            letters = string.ascii_lowercase[:self.alpha]
            self.text = "".join(random.choice(letters) for _ in range(self.n))
            self.answer = self._lps(self.text)

    @staticmethod
    def _lis(seq: List[int]) -> int:
        if not seq:
            return 0
        dp = [1] * len(seq)
        for i in range(len(seq)):
            for j in range(i):
                if seq[j] < seq[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    @staticmethod
    def _lps(s: str) -> int:
        n = len(s)
        if n == 0:
            return 0
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    dp[i][j] = (dp[i + 1][j - 1] if length > 2 else 0) + 2
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1]

    def _descr(self, language):
        if self.task_type == "lis":
            arr = ", ".join(map(str, self.seq))
            return ((texts.t('s1', language, arr=arr)))
        return ((texts.t('s0', language, text=self.text)))

    def solve(self):
        if self.task_type == "lis":
            self.solution_steps = [
                texts.t("literals.s2", self.language)]
        else:
            self.solution_steps = [
                texts.t("literals.s3", self.language)]
        self.solution_steps.append(
            ((texts.common('answer_line', self.language, answer=self.answer))))
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
