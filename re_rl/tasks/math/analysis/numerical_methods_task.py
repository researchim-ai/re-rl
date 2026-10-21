"""NumericalMethodsTask — один шаг численных методов с однозначным ответом.

Подтипы:
- ``newton``    — следующий шаг метода Ньютона для f(x) = (x - r)^2, ответ целый;
- ``trapezoid`` — приближение интеграла f(x) = x^2 методом трапеций, h = 1
  (ответ — целое или дробь вида a/2);
- ``bisection`` — левый конец отрезка после k шагов бисекции для f(x) = x - root.
  Середина [L, R] равна (L + R) // 2. Если f(L) * f(середина) <= 0, новый отрезок
  [L, середина], иначе [середина, R].
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class NumericalMethodsTask(BaseMathTask):
    TASK_TYPE = "numerical_methods"
    TASK_TYPES = ["newton", "trapezoid", "bisection"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"span": 16, "steps": 2, "panels": 2},
        2: {"span": 16, "steps": 2, "panels": 2},
        3: {"span": 16, "steps": 3, "panels": 3},
        4: {"span": 32, "steps": 3, "panels": 3},
        5: {"span": 32, "steps": 4, "panels": 4},
        6: {"span": 32, "steps": 4, "panels": 4},
        7: {"span": 64, "steps": 5, "panels": 5},
        8: {"span": 64, "steps": 5, "panels": 6},
        9: {"span": 64, "steps": 6, "panels": 7},
        10: {"span": 64, "steps": 6, "panels": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.span = int(p["span"])
        self.steps = int(p["steps"])
        self.panels = int(p["panels"])
        self.difficulty = difficulty
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @staticmethod
    def newton_step(r: int, x0: int) -> int:
        f = (x0 - r) ** 2
        fp = 2 * (x0 - r)
        if fp == 0 or f % fp != 0:
            raise ValueError("шаг Ньютона должен быть целым")
        return x0 - f // fp

    @staticmethod
    def trapezoid(a: int, n: int) -> Tuple[List[int], int]:
        """Возвращает (значения f, удвоенное приближение). Приближение = acc/2."""
        ys = [(a + i) ** 2 for i in range(n + 1)]
        acc = ys[0] + ys[-1] + 2 * sum(ys[1:-1])
        return ys, acc

    @staticmethod
    def bisection_left(root: int, span: int, steps: int) -> List[Tuple[int, int]]:
        lo, hi = 0, span
        hist = [(lo, hi)]
        for _ in range(steps):
            mid = (lo + hi) // 2
            if (lo - root) * (mid - root) <= 0:
                hi = mid
            else:
                lo = mid
            hist.append((lo, hi))
        return hist

    def _build(self):
        if self.task_type == "newton":
            self.r = random.randint(1, 4 + int(self.difficulty))
            self.x0 = self.r + 2 * random.randint(1, 3)
            self.answer = self.newton_step(self.r, self.x0)
            self.value = float(self.answer)
        elif self.task_type == "trapezoid":
            self.a0 = random.randint(0, 3)
            self.ys, self.acc = self.trapezoid(self.a0, self.panels)
            self.value = self.acc / 2
            self.answer = str(self.acc // 2) if self.acc % 2 == 0 else f"{self.acc}/2"
        else:
            self.root = random.randint(1, self.span - 1)
            self.hist = self.bisection_left(self.root, self.span, self.steps)
            self.answer = self.hist[-1][0]
            self.value = float(self.answer)

    def _poly(self) -> str:
        b = 2 * self.r
        c = self.r * self.r
        return f"x^2 - {b}x + {c}"

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "newton":
            return ((f"Функция f(x) = {self._poly()}. Сделайте один шаг метода Ньютона из точки "
                     f"x0 = {self.x0}: x1 = x0 - f(x0) / f'(x0). Чему равен x1?") if ru else
                    (f"Let f(x) = {self._poly()}. Take one Newton step from x0 = {self.x0}: "
                     f"x1 = x0 - f(x0) / f'(x0). What is x1?"))
        if self.task_type == "trapezoid":
            b = self.a0 + self.panels
            return ((f"Приблизьте интеграл f(x) = x^2 на отрезке [{self.a0}, {b}] методом трапеций "
                     f"с шагом h = 1 ({self.panels} отрезков). Ответ — число, при необходимости дробь a/2.")
                    if ru else
                    (f"Approximate the integral of f(x) = x^2 on [{self.a0}, {b}] by the trapezoidal "
                     f"rule with step h = 1 ({self.panels} panels). Answer with a number, or a fraction a/2."))
        return ((f"f(x) = x - {self.root}. Отрезок [0, {self.span}]. Середина [L, R] — это (L+R)//2. "
                 f"Если f(L)*f(середина) <= 0, новый отрезок [L, середина], иначе [середина, R]. "
                 f"Чему равен левый конец после {self.steps} шагов?") if ru else
                (f"f(x) = x - {self.root}. Start from [0, {self.span}]. The midpoint of [L, R] is "
                 f"(L+R)//2. If f(L)*f(mid) <= 0 the new interval is [L, mid], otherwise [mid, R]. "
                 f"What is the left endpoint after {self.steps} steps?"))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "newton":
            f = (self.x0 - self.r) ** 2
            fp = 2 * (self.x0 - self.r)
            step = ((f"f({self.x0}) = {f}, f'({self.x0}) = {fp}, "
                     f"x1 = {self.x0} - {f}/{fp} = {self.answer}.") if ru else
                    (f"f({self.x0}) = {f}, f'({self.x0}) = {fp}, "
                     f"x1 = {self.x0} - {f}/{fp} = {self.answer}."))
            shown = str(self.answer)
        elif self.task_type == "trapezoid":
            ys = ", ".join(map(str, self.ys))
            step = ((f"Значения f на узлах: {ys}. Сумма с коэффициентами = {self.acc}, "
                     f"делим на 2 и получаем {self.answer}.") if ru else
                    (f"f at the nodes: {ys}. The weighted sum is {self.acc}; "
                     f"dividing by 2 gives {self.answer}."))
            shown = self.answer
        else:
            parts = [f"[{lo}, {hi}]" for lo, hi in self.hist]
            step = ((f"Отрезки: {' -> '.join(parts)}.") if ru else
                    (f"Intervals: {' -> '.join(parts)}."))
            shown = str(self.answer)
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "trapezoid":
            return U.verify_value(prediction, float(self.value), tol=1e-6)
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
