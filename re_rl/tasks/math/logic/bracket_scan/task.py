"""BracketScanTask — глубина скобок и место первой ошибки.

Длина строки растёт с уровнем. 0 значит, что строка корректна.
Лишняя закрывающая даёт свой номер, незакрытые открывающие — номер на единицу больше длины.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _scan(chars: str):
    depth = 0
    max_depth = 0
    error = 0
    depths: List[int] = []
    for index, char in enumerate(chars, 1):
        if char == "(":
            depth += 1
            if error == 0:
                max_depth = max(max_depth, depth)
        else:
            depth -= 1
            if depth < 0 and error == 0:
                error = index
        depths.append(depth)
    if error == 0 and depth != 0:
        error = len(chars) + 1
    return depths, max_depth, error


class BracketScanTask(BaseMathTask):
    TASK_TYPE = "bracket_scan"
    TASK_TYPES = ["depth", "error"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5}, 5: {"n": 6},
        6: {"n": 8}, 7: {"n": 8}, 8: {"n": 10}, 9: {"n": 12}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        chars: List[str] = []
        depth = 0
        for _ in range(self.n):
            if depth == 0 or random.random() < 0.55:
                chars.append("(")
                depth += 1
            else:
                chars.append(")")
                depth -= 1
        if random.random() < 0.5:
            index = random.randrange(self.n)
            chars[index] = ")" if chars[index] == "(" else "("
        self.expr = "".join(chars)
        self.depths, self.max_depth, self.error = _scan(self.expr)
        self.answer = self.max_depth if self.task_type == "depth" else self.error
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "depth" else "s1"
        return texts.t(key, language, n=self.n, expr=self.expr, n_plus=self.n + 1)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=i, char=char, depth=depth)
            for i, (char, depth) in enumerate(zip(self.expr, self.depths), 1)
        ]
        steps.append(texts.t("s3", self.language, depth=self.max_depth, error=self.error))
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
