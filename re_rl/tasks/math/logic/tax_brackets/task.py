"""TaxBracketsTask — налог по ступеням дохода.

Доход заполняет ступени по порядку. Процент берётся только с попавшей в ступень части.
Ширины кратны 20, поэтому налог целый. Число ступеней растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

RATES = (0, 10, 20, 25, 50)
Bracket = Tuple[int, int]


def apply_tax(income: int, brackets: Sequence[Bracket]):
    left = income
    tax = 0
    band = 0
    trace = []
    for index, (width, rate) in enumerate(brackets, 1):
        piece = min(left, width)
        assert piece * rate % 100 == 0
        part = piece * rate // 100
        tax += part
        left -= piece
        if piece:
            band = index
        trace.append((piece, part, tax, left))
    return tax, band, trace


class TaxBracketsTask(BaseMathTask):
    TASK_TYPE = "tax_brackets"
    TASK_TYPES = ["tax", "band"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.brackets: List[Bracket] = [
            (20 * random.randint(1, 4), random.choice(RATES)) for _ in range(self.n)
        ]
        cut = random.randrange(self.n)
        self.income = sum(width for width, _rate in self.brackets[:cut])
        self.income += random.randrange(20, self.brackets[cut][0] + 1, 20)
        self.tax, self.band, self.trace = apply_tax(self.income, self.brackets)
        self.answer = self.tax if self.task_type == "tax" else self.band
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{width}/{rate}" for width, rate in self.brackets)
        key = "s0" if self.task_type == "tax" else "s1"
        return texts.t(key, language, income=self.income, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, piece=piece, rate=rate, part=part, tax=tax)
            for index, ((piece, part, tax, _left), (_width, rate)) in enumerate(
                zip(self.trace, self.brackets), 1,
            )
        ]
        steps.append(texts.t("s3", self.language, tax=self.tax, band=self.band))
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
