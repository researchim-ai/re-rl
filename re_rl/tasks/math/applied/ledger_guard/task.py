"""LedgerGuardTask — счёт, на котором слишком большое снятие отклоняется.

Число операций растёт с уровнем. Отклонённое снятие не меняет баланс, поэтому порядок важен.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class LedgerGuardTask(BaseMathTask):
    TASK_TYPE = "ledger_guard"
    TASK_TYPES = ["balance", "rejected"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "v": 6}, 2: {"n": 3, "v": 8}, 3: {"n": 4, "v": 8},
        4: {"n": 4, "v": 10}, 5: {"n": 5, "v": 10}, 6: {"n": 6, "v": 12},
        7: {"n": 7, "v": 12}, 8: {"n": 8, "v": 15}, 9: {"n": 9, "v": 16},
        10: {"n": 10, "v": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["v"])
        self.start = random.randint(0, limit)
        self.balance = self.start
        self.rejected = 0
        self.ops: List[Dict[str, int]] = []
        for _ in range(self.n):
            amount = random.randint(1, limit)
            incoming = random.random() < 0.45
            if incoming:
                self.balance += amount
                self.ops.append({"sign": 1, "amount": amount, "balance": self.balance, "rejected": 0})
            elif amount > self.balance:
                self.rejected += 1
                self.ops.append({"sign": -1, "amount": amount, "balance": self.balance, "rejected": 1})
            else:
                self.balance -= amount
                self.ops.append({"sign": -1, "amount": amount, "balance": self.balance, "rejected": 0})
        self.answer = self.balance if self.task_type == "balance" else self.rejected
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = []
        for index, op in enumerate(self.ops, 1):
            sign = "+" if op["sign"] > 0 else "-"
            parts.append(texts.t("s2", language, i=index, sign=sign, amount=op["amount"]))
        key = "s0" if self.task_type == "balance" else "s1"
        return texts.t(key, language, start=self.start, n=self.n, listing=" ".join(parts))

    def solve(self):
        steps = []
        for index, op in enumerate(self.ops, 1):
            sign = "+" if op["sign"] > 0 else "-"
            flag = texts.t("s5" if op["rejected"] else "s4", self.language)
            steps.append(texts.t(
                "s3", self.language, i=index, sign=sign, amount=op["amount"],
                balance=op["balance"], flag=flag,
            ))
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
