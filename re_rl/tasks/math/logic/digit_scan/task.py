"""DigitScanTask — чтение десятичного числа до стоп-символа.

Цифры от 0 до 9 дописываются справа. Отрицательное число останавливает чтение, само в число не входит.
Число символов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def scan_trace(tokens: Sequence[int]) -> List[Tuple[int, int, int]]:
    value = 0
    length = 0
    stopped = 0
    done = False
    trace = []
    for index, token in enumerate(tokens, 1):
        if not done:
            if token < 0:
                done = True
                stopped = index
            else:
                value = value * 10 + token
                length += 1
        trace.append((value, length, stopped))
    return trace


class DigitScanTask(BaseMathTask):
    TASK_TYPE = "digit_scan"
    TASK_TYPES = ["value", "length"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.tokens = []
        for _ in range(self.n):
            if random.random() < 0.25:
                self.tokens.append(-1)
            else:
                self.tokens.append(random.randint(0, 9))
        self.trace = scan_trace(self.tokens)
        self.value = self.trace[-1][0]
        self.length = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.length
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(token) for token in self.tokens)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, tokens=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, token=token, value=value, length=length, stop=stop)
            for index, (token, (value, length, stop)) in enumerate(zip(self.tokens, self.trace), 1)
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
