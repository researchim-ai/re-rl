"""Countdown24Task — «игра в числа»: собрать целевое число из набора.

Дан набор чисел и цель. Нужно составить арифметическое выражение (+ − × ÷,
каждое число используется ровно один раз), равное цели. Экземпляр строится из
случайного выражения, поэтому решение гарантированно существует. Проверка —
собственный безопасный вычислитель: ответ принимается, если использует ровно
заданные числа и равен цели.
"""

import random
from collections import Counter
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class Countdown24Task(BaseMathTask):
    TASK_TYPE = "countdown_24"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "hi": 6}, 2: {"n": 3, "hi": 9}, 3: {"n": 4, "hi": 9},
        4: {"n": 4, "hi": 10}, 5: {"n": 4, "hi": 12}, 6: {"n": 5, "hi": 10},
        7: {"n": 5, "hi": 12}, 8: {"n": 5, "hi": 15}, 9: {"n": 6, "hi": 12},
        10: {"n": 6, "hi": 15},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.hi = int(preset["hi"])
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        for _ in range(200):
            self.numbers = [random.randint(1, self.hi) for _ in range(self.n)]
            items = [(v, str(v)) for v in self.numbers]
            ok = True
            while len(items) > 1:
                i, j = random.sample(range(len(items)), 2)
                (va, ea), (vb, eb) = items[i], items[j]
                ops = ["+", "-", "*"]
                if vb != 0 and va % vb == 0:
                    ops.append("/")
                op = random.choice(ops)
                if op == "+":
                    val = va + vb
                elif op == "-":
                    val = va - vb
                elif op == "*":
                    val = va * vb
                else:
                    val = va // vb
                expr = f"({ea} {op} {eb})"
                items = [it for idx, it in enumerate(items) if idx not in (i, j)]
                items.append((val, expr))
            value, expr = items[0]
            if 1 <= value <= 1000:
                self.target = value
                self.expr = expr
                ok = True
                break
        else:
            # предельный случай: просто сумма
            self.numbers = [random.randint(1, self.hi) for _ in range(self.n)]
            self.target = sum(self.numbers)
            self.expr = "(" + " + ".join(str(v) for v in self.numbers) + ")"

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        nums = ", ".join(str(v) for v in self.numbers)
        return ((f"Используя каждое из чисел {nums} ровно один раз и операции + − × ÷ "
                 f"(со скобками), составьте выражение, равное {self.target}.") if ru else
                (f"Using each of the numbers {nums} exactly once and the operations + − × ÷ "
                 f"(with parentheses), build an expression equal to {self.target}."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Комбинируем числа операциями, пока не получим цель." if ru else
             "Combine the numbers with operations until the target is reached."),
            (f"Пример: {self.expr} = {self.target}." if ru else
             f"Example: {self.expr} = {self.target}."),
        ]
        self.final_answer = f"{self.expr} = {self.target}"

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        text = U.clean(prediction)
        if "=" in text:
            text = text.split("=")[0]
        val = U.safe_eval(text)
        if val is None:
            return 0.0
        if Counter(U.numbers_in_expr(text)) != Counter(self.numbers):
            return 0.0
        return 1.0 if abs(val - self.target) < 1e-6 else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
