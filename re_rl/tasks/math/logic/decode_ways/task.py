"""DecodeWaysTask — число способов разбить строку цифр на коды букв.

1..26 соответствуют буквам. Ноль не кодируется отдельно.
Пара считается, только если это число от 10 до 26.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def num_decodings(code: str) -> int:
    if not code or code[0] == "0":
        return 0
    prev2, prev1 = 1, 1
    for i in range(1, len(code)):
        ways = 0
        if code[i] != "0":
            ways += prev1
        pair = int(code[i - 1:i + 1])
        if 10 <= pair <= 26:
            ways += prev2
        prev2, prev1 = prev1, ways
    return prev1


class DecodeWaysTask(BaseMathTask):
    TASK_TYPE = "decode_ways"
    TASK_TYPES = ["count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 3}, 3: {"n": 3}, 4: {"n": 4}, 5: {"n": 4},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = "count"
        self.augment = augment
        self.code = self._make_code(self.n)
        self.answer = num_decodings(self.code)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @staticmethod
    def _make_code(n: int) -> str:
        digits = []
        while len(digits) < n:
            if random.random() < 0.35 and len(digits) + 2 <= n:
                pair = random.randint(10, 26)
                digits.extend(list(f"{pair:02d}"))
            else:
                digits.append(str(random.randint(1, 9)))
        return "".join(digits[:n])

    def _descr(self, language):
        return ((texts.t('s0', language, code=self.code)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language, answer=self.answer))),
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
