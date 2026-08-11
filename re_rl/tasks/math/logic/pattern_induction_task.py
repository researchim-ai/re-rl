"""PatternInductionTask — индуктивный вывод правила числовой последовательности.

Даны первые несколько членов, нужно назвать следующий. Правило (арифметическое,
геометрическое, квадратичное, рекуррентное типа Фибоначчи, знакочередующееся)
задаётся генератором детерминированно.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class PatternInductionTask(BaseMathTask):
    TASK_TYPE = "pattern_induction"
    TASK_TYPES = ["arithmetic", "geometric", "quadratic", "fibonacci_like", "alternating"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"terms": 5, "scale": 3}, 2: {"terms": 5, "scale": 4}, 3: {"terms": 5, "scale": 5},
        4: {"terms": 6, "scale": 6}, 5: {"terms": 6, "scale": 8}, 6: {"terms": 6, "scale": 10},
        7: {"terms": 7, "scale": 12}, 8: {"terms": 7, "scale": 15}, 9: {"terms": 7, "scale": 20},
        10: {"terms": 8, "scale": 25},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.terms = int(preset["terms"])
        self.scale = int(preset["scale"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _gen(self, i: int) -> int:
        p = self.params
        if self.subtype == "arithmetic":
            return p["a0"] + p["d"] * i
        if self.subtype == "geometric":
            return p["a0"] * p["r"] ** i
        if self.subtype == "quadratic":
            return p["a"] * i * i + p["b"] * i + p["c"]
        if self.subtype == "alternating":
            return ((-1) ** i) * (p["base"] + p["d"] * i)
        return 0  # fibonacci_like обрабатывается отдельно

    def _build(self):
        s = self.scale
        if self.subtype == "arithmetic":
            self.params = {"a0": random.randint(-s, s), "d": random.randint(1, s)}
            self.seq = [self._gen(i) for i in range(self.terms + 1)]
            self.rule = "arithmetic"
        elif self.subtype == "geometric":
            self.params = {"a0": random.randint(1, max(2, s // 2)), "r": random.randint(2, 3)}
            self.seq = [self._gen(i) for i in range(self.terms + 1)]
            self.rule = "geometric"
        elif self.subtype == "quadratic":
            self.params = {"a": random.randint(1, 3), "b": random.randint(-s, s),
                           "c": random.randint(-s, s)}
            self.seq = [self._gen(i) for i in range(self.terms + 1)]
            self.rule = "quadratic"
        elif self.subtype == "alternating":
            self.params = {"base": random.randint(1, s), "d": random.randint(1, max(1, s // 2))}
            self.seq = [self._gen(i) for i in range(self.terms + 1)]
            self.rule = "alternating"
        else:  # fibonacci_like
            t0, t1 = random.randint(1, s), random.randint(1, s)
            p, q = random.choice([(1, 1), (2, 1), (1, 2)])
            self.params = {"t0": t0, "t1": t1, "p": p, "q": q}
            seq = [t0, t1]
            for _ in range(self.terms - 1):
                seq.append(p * seq[-1] + q * seq[-2])
            self.seq = seq
            self.rule = "fibonacci_like"

        self.given = self.seq[:self.terms]
        self._answer = self.seq[self.terms]

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        shown = ", ".join(str(x) for x in self.given)
        return (f"Дана последовательность: {shown}, ... Найдите следующий член." if ru else
                f"Given the sequence: {shown}, ... Find the next term.")

    def solve(self):
        ru = self.language == "ru"
        names = {
            "arithmetic": ("арифметическая прогрессия", "arithmetic progression"),
            "geometric": ("геометрическая прогрессия", "geometric progression"),
            "quadratic": ("квадратичная зависимость", "quadratic rule"),
            "fibonacci_like": ("рекуррента типа Фибоначчи", "Fibonacci-like recurrence"),
            "alternating": ("знакочередующаяся последовательность", "alternating sequence"),
        }
        nm = names[self.rule][0 if ru else 1]
        self.solution_steps = [
            (f"Определяем закономерность: {nm}." if ru else f"Identify the pattern: {nm}."),
            (f"Следующий член = {self._answer}." if ru else f"Next term = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
