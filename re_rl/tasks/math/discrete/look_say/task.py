"""LookSayTask — несколько шагов «посмотри и скажи».

Каждая серия одинаковых цифр заменяется на длину серии и саму цифру.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def look_say_once(word: str) -> str:
    parts = []
    index = 0
    while index < len(word):
        end = index + 1
        while end < len(word) and word[end] == word[index]:
            end += 1
        parts.append(str(end - index) + word[index])
        index = end
    return "".join(parts)


def look_say_trace(start: str, rounds: int) -> List[str]:
    word = start
    trace = []
    for _ in range(rounds):
        word = look_say_once(word)
        trace.append(word)
    return trace


class LookSayTask(BaseMathTask):
    TASK_TYPE = "look_say"
    TASK_TYPES = ["length", "digit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 9},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.start = str(random.randint(1, 9))
        self.trace = look_say_trace(self.start, self.n)
        self.word = self.trace[-1]
        self.length = len(self.word)
        self.digit = random.randint(1, 9)
        self.count = self.word.count(str(self.digit))
        self.answer = self.length if self.task_type == "length" else self.count
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "length" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, digit=self.digit)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, word=word, length=len(word))
            for index, word in enumerate(self.trace, 1)
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
