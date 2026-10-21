"""SubsequenceCountTask — число вхождений шаблона как подпоследовательности.

Позиции строго возрастают, буквы не обязаны стоять подряд.
Шаблон сам является подпоследовательностью текста, поэтому ответ хотя бы 1.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ALPHABET = "abc"


def count_subsequence(text: str, pattern: str) -> int:
    ways = [0] * (len(pattern) + 1)
    ways[0] = 1
    for char in text:
        for index in range(len(pattern), 0, -1):
            if char == pattern[index - 1]:
                ways[index] += ways[index - 1]
    return ways[-1]


class SubsequenceCountTask(BaseMathTask):
    TASK_TYPE = "subsequence_count"
    TASK_TYPES = ["ways"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6, "k": 2}, 2: {"n": 7, "k": 2}, 3: {"n": 8, "k": 3},
        4: {"n": 9, "k": 3}, 5: {"n": 10, "k": 3}, 6: {"n": 12, "k": 4},
        7: {"n": 13, "k": 4}, 8: {"n": 15, "k": 4}, 9: {"n": 16, "k": 5},
        10: {"n": 18, "k": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["n"])
        self.pattern_len = int(p["k"])
        self.task_type = "ways"
        self.augment = augment
        self.text = "".join(random.choice(_ALPHABET) for _ in range(self.length))
        picked = sorted(random.sample(range(self.length), self.pattern_len))
        self.pattern = "".join(self.text[index] for index in picked)
        self.answer = count_subsequence(self.text, self.pattern)
        if self.answer < 1:
            raise RuntimeError(texts.t('s2', language))
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        return ((texts.t('s0', language, text=self.text, pattern=self.pattern)))

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
