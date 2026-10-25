"""BracePairTask — круглые и квадратные скобки.

0 открывает круглую, 1 закрывает круглую, 2 открывает квадратную, 3 закрывает квадратную.
Закрытие не той скобки — ошибка, стек при этом не снимается.
Число скобок растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

PAIRS = {1: 0, 3: 2}


def brace_trace(tokens: Sequence[int]) -> Tuple[List[Tuple[int, int]], int]:
    stack: List[int] = []
    errors = 0
    trace = []
    for token in tokens:
        if token in (0, 2):
            stack.append(token)
        else:
            need = PAIRS[token]
            if stack and stack[-1] == need:
                stack.pop()
            else:
                errors += 1
        trace.append((len(stack), errors))
    return trace, len(stack)


class BracePairTask(BaseMathTask):
    TASK_TYPE = "brace_pair"
    TASK_TYPES = ["errors", "open"]

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
        self.tokens = [random.choice((0, 1, 2, 3)) for _ in range(self.n)]
        self.trace, self.open = brace_trace(self.tokens)
        self.errors = self.trace[-1][1]
        self.answer = self.errors if self.task_type == "errors" else self.open
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(token) for token in self.tokens)
        key = "s0" if self.task_type == "errors" else "s1"
        return texts.t(key, language, n=self.n, tokens=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, token=token, depth=depth, errors=errors)
            for index, (token, (depth, errors)) in enumerate(zip(self.tokens, self.trace), 1)
        ]
        steps.append(texts.t("s3", self.language, errors=self.errors, open=self.open))
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
