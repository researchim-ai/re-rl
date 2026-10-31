"""FindTheErrorTask — найти шаг с ошибкой в цепочке вычислений.

Дано решение из нескольких независимых арифметических равенств, ровно одно из
которых содержит ошибку. Нужно назвать номер ошибочного шага. Ответ — целое
число, поэтому задача легко и однозначно верифицируется.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class FindTheErrorTask(BaseMathTask):
    """Найти номер шага с арифметической ошибкой."""

    TASK_TYPE = texts.literal('literals.s0')

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_steps": 3, "max_number": 10, "ops": ["+", "-"]},
        2: {"num_steps": 3, "max_number": 15, "ops": ["+", "-"]},
        3: {"num_steps": 4, "max_number": 20, "ops": ["+", "-", "*"]},
        4: {"num_steps": 4, "max_number": 30, "ops": ["+", "-", "*"]},
        5: {"num_steps": 5, "max_number": 40, "ops": ["+", "-", "*"]},
        6: {"num_steps": 5, "max_number": 60, "ops": ["+", "-", "*"]},
        7: {"num_steps": 6, "max_number": 80, "ops": ["+", "-", "*"]},
        8: {"num_steps": 6, "max_number": 100, "ops": ["+", "-", "*"]},
        9: {"num_steps": 7, "max_number": 120, "ops": ["+", "-", "*"]},
        10: {"num_steps": 8, "max_number": 150, "ops": ["+", "-", "*"]},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_steps: Optional[int] = None,
        max_number: Optional[int] = None,
        ops=None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_steps = num_steps if num_steps is not None else preset["num_steps"]
        self.max_number = max_number if max_number is not None else preset["max_number"]
        if type(self.num_steps) is not int or not 1 <= self.num_steps <= 1000:
            raise ValueError("invalid_num_steps")
        if type(self.max_number) is not int or not 1 <= self.max_number <= 1_000_000:
            raise ValueError("invalid_max_number")
        self.ops = list(preset["ops"]) if ops is None else ops
        if not isinstance(self.ops,(list,tuple)) or not self.ops or any(op not in ("+","-","*") for op in self.ops):
            raise ValueError("invalid_operators")
        self.augment = augment

        # Каждый шаг: (a, op, b, shown_value, correct_value)
        self._steps: List[Tuple[int, str, int, int, int]] = []
        self._error_index: int = 0
        self._build_steps()

        section = PROMPT_TEMPLATES[texts.t('s1', language)]
        step_label = get_template(section, "step_label", language, augment=False)
        lines = []
        for i, (a, op, b, shown, _correct) in enumerate(self._steps, start=1):
            lines.append(f"{step_label} {i}: {a} {op} {b} = {shown}")
        steps_text = "\n".join(lines)

        description = get_template(section, "problem", language, augment=augment, steps=steps_text)
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    @staticmethod
    def _compute(a: int, op: str, b: int) -> int:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":return a * b
        raise ValueError("invalid_operator")

    def _build_steps(self):
        self._steps = []
        for _ in range(self.num_steps):
            op = random.choice(self.ops)
            a = random.randint(1, self.max_number)
            b = random.randint(1, self.max_number)
            correct = self._compute(a, op, b)
            self._steps.append((a, op, b, correct, correct))

        # Портим ровно один шаг.
        self._error_index = random.randint(1, len(self._steps))
        a, op, b, _shown, correct = self._steps[self._error_index - 1]
        delta = random.choice([d for d in (-3, -2, -1, 1, 2, 3)])
        wrong = correct + delta
        while wrong == correct:
            wrong = correct + random.choice([-1, 1])
        self._steps[self._error_index - 1] = (a, op, b, wrong, correct)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        import re
        from re_rl.tasks.math.logic import _logic_utils as U
        self.solve()
        value=U.clean(prediction).strip()
        section=PROMPT_TEMPLATES[self.TASK_TYPE]
        labels=[get_template(section,"step_label",lang,augment=False) for lang in ("ru","en")]
        prefix="(?:"+"|".join(re.escape(label) for label in labels)+r")(?:\s*:\s*|\s+)"
        match=re.fullmatch("(?:"+prefix+r")?(\d+)",value,re.IGNORECASE)
        if not match:return 0.0
        try:return float(int(match.group(1))==int(self.final_answer))
        except ValueError:return 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "FindTheErrorTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
