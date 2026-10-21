"""EulerMethodTask — метод Эйлера для y' = px + qy + r с целым шагом h = 1.

При целых коэффициентах и целых начальных данных все узлы остаются целыми,
поэтому ответ точный, без накопления погрешности представления.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def format_rhs(p: int, q: int, r: int) -> str:
    """Правая часть px + qy + r без лишних единиц и со знаками."""
    parts: List[str] = []

    def push(coef: int, body: str):
        if coef == 0:
            return
        mag = abs(coef)
        token = body if mag == 1 else f"{mag}{body}"
        if not parts:
            parts.append(token if coef > 0 else f"-{token}")
        else:
            parts.append(("+ " if coef > 0 else "- ") + token)

    push(p, "x")
    push(q, "y")
    if r != 0:
        if not parts:
            parts.append(str(r))
        else:
            parts.append(("+ " if r > 0 else "- ") + str(abs(r)))
    return " ".join(parts) if parts else "0"


def euler_trace(x: int, y: int, p: int, q: int, r: int, steps: int) -> List[Tuple[int, int]]:
    """Узлы после каждого шага, включая начальный (x0, y0)."""
    trace = [(x, y)]
    for _ in range(steps):
        y = y + (p * x + q * y + r)
        x = x + 1
        trace.append((x, y))
    return trace


class EulerMethodTask(BaseMathTask):
    TASK_TYPE = "euler_method"
    TASK_TYPES = ["one_step", "multi_step"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"steps": 1, "coef": 1}, 2: {"steps": 2, "coef": 1},
        3: {"steps": 2, "coef": 2}, 4: {"steps": 3, "coef": 2},
        5: {"steps": 3, "coef": 2}, 6: {"steps": 4, "coef": 2},
        7: {"steps": 4, "coef": 3}, 8: {"steps": 5, "coef": 2},
        9: {"steps": 5, "coef": 3}, 10: {"steps": 6, "coef": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.max_steps = int(p["steps"])
        self.coef = int(p["coef"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.steps = 1 if self.task_type == "one_step" else self.max_steps
        self.p = random.randint(-self.coef, self.coef)
        self.q = random.randint(-self.coef, self.coef)
        self.r = random.randint(-self.coef, self.coef)
        if self.p == 0 and self.q == 0 and self.r == 0:
            self.q = 1
        self.x0 = random.randint(-2, 3)
        self.y0 = random.randint(-3, 4)
        self.trace = euler_trace(self.x0, self.y0, self.p, self.q, self.r, self.steps)
        self.answer = self.trace[-1][1]

    def _descr(self, language):
        ru = language == "ru"
        rhs = format_rhs(self.p, self.q, self.r)
        rule = (("Шаг метода Эйлера: y_new = y + h*f(x, y), x_new = x + h, h = 1.") if ru else
                ("One Euler step is y_new = y + h*f(x, y), x_new = x + h, with h = 1."))
        if ru:
            word = "шага" if self.steps % 10 == 1 and self.steps % 100 != 11 else "шагов"
            ask = (f"Дано y' = {rhs}, y({self.x0}) = {self.y0}. "
                   f"Чему равно y после {self.steps} {word}?")
        else:
            word = "step" if self.steps == 1 else "steps"
            ask = (f"Given y' = {rhs}, y({self.x0}) = {self.y0}. "
                   f"What is y after {self.steps} {word}?")
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        bits = []
        for i in range(1, len(self.trace)):
            x_prev, y_prev = self.trace[i - 1]
            x_new, y_new = self.trace[i]
            slope = self.p * x_prev + self.q * y_prev + self.r
            bits.append(f"({x_prev}, {y_prev}) -> ({x_new}, {y_new}), f = {slope}")
        self.solution_steps = [
            (("Узлы: " if ru else "Nodes: ") + "; ".join(bits) + "."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
