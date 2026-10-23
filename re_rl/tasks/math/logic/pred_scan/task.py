"""PredScanTask — проверка ряда сравнений и место первой ошибки.

Каждое сравнение смотрит два числа и один знак. Проход линейный.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pred = Tuple[int, str, int]
SIGNS = ("<", "=", ">")


def holds(pred: Pred) -> bool:
    left, sign, right = pred
    if sign == "<":
        return left < right
    if sign == "=":
        return left == right
    return left > right


def pred_trace(preds: Sequence[Pred]) -> List[Tuple[int, int]]:
    true = 0
    first = 0
    trace = []
    for index, pred in enumerate(preds, 1):
        if holds(pred):
            true += 1
        elif first == 0:
            first = index
        trace.append((true, first))
    return trace


class PredScanTask(BaseMathTask):
    TASK_TYPE = "pred_scan"
    TASK_TYPES = ["trues", "first"]

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
        self.preds = [
            (random.randint(0, 12), random.choice(SIGNS), random.randint(0, 12))
            for _ in range(self.n)
        ]
        self.trace = pred_trace(self.preds)
        self.trues, self.first = self.trace[-1]
        self.answer = self.trues if self.task_type == "trues" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _text(self, pred: Pred) -> str:
        left, sign, right = pred
        return f"{left} {sign} {right}"

    def _descr(self, language):
        listing = "; ".join(self._text(pred) for pred in self.preds)
        key = "s0" if self.task_type == "trues" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, pred=self._text(pred), trues=true, first=first)
            for index, (pred, (true, first)) in enumerate(zip(self.preds, self.trace), 1)
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
