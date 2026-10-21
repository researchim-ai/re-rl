"""Алгоритм Кнута — Морриса — Пратта (KMP).

Подтипы:
- ``failure_function`` — префикс-функция образца (массив значений);
- ``occurrences``      — число вхождений образца в текст (с перекрытиями).

Масштаб задаётся длиной образца/текста и размером алфавита.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import string
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U


class KMPMatchingTask(BaseMathTask):
    TASK_TYPE = "kmp_matching"
    TASK_TYPES = ["failure_function", "occurrences"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 3, "t": 8, "alpha": 2}, 2: {"m": 3, "t": 10, "alpha": 2},
        3: {"m": 4, "t": 12, "alpha": 2}, 4: {"m": 4, "t": 14, "alpha": 3},
        5: {"m": 5, "t": 16, "alpha": 3}, 6: {"m": 5, "t": 20, "alpha": 3},
        7: {"m": 6, "t": 24, "alpha": 3}, 8: {"m": 6, "t": 28, "alpha": 4},
        9: {"m": 7, "t": 32, "alpha": 4}, 10: {"m": 8, "t": 40, "alpha": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.m, self.t, self.alpha = int(p["m"]), int(p["t"]), int(p["alpha"])
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        letters = string.ascii_lowercase[:self.alpha]
        self.pattern = "".join(random.choice(letters) for _ in range(self.m))
        if self.task_type == "failure_function":
            self.pi = self._prefix_function(self.pattern)
        else:
            self.text = "".join(random.choice(letters) for _ in range(self.t))
            self.count = self._count_occurrences(self.text, self.pattern)

    @staticmethod
    def _prefix_function(s: str) -> List[int]:
        pi = [0] * len(s)
        k = 0
        for i in range(1, len(s)):
            while k > 0 and s[i] != s[k]:
                k = pi[k - 1]
            if s[i] == s[k]:
                k += 1
            pi[i] = k
        return pi

    def _count_occurrences(self, text: str, pat: str) -> int:
        pi = self._prefix_function(pat)
        k = 0
        cnt = 0
        for i in range(len(text)):
            while k > 0 and text[i] != pat[k]:
                k = pi[k - 1]
            if text[i] == pat[k]:
                k += 1
            if k == len(pat):
                cnt += 1
                k = pi[k - 1]
        return cnt

    def _descr(self, language):
        if self.task_type == "failure_function":
            idx = ", ".join(str(i) for i in range(len(self.pattern)))
            return ((texts.t('s1', language, pattern=self.pattern, idx=idx, v2=len(self.pattern) - 1)))
        return ((texts.t('s0', language, pattern=self.pattern, text=self.text)))

    def solve(self):
        if self.task_type == "failure_function":
            arr = ", ".join(map(str, self.pi))
            self.solution_steps = [
                texts.t("literals.s2", self.language),
                ((f"π = [{arr}]."))]
            self.final_answer = arr
        else:
            self.solution_steps = [
                ((texts.t('s3', self.language))),
                ((texts.t('s4', self.language, count=self.count)))]
            self.final_answer = str(self.count)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "failure_function":
            return U.verify_int_sequence(prediction, self.pi)
        return U.verify_int(prediction, int(self.count))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
