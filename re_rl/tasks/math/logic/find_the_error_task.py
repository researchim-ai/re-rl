"""FindTheErrorTask — найти шаг с ошибкой в цепочке вычислений.

Дано решение из нескольких независимых арифметических равенств, ровно одно из
которых содержит ошибку. Нужно назвать номер ошибочного шага. Ответ — целое
число, поэтому задача легко и однозначно верифицируется.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class FindTheErrorTask(BaseMathTask):
    """Найти номер шага с арифметической ошибкой."""

    TASK_TYPE = "find_the_error"

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
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_steps = int(num_steps if num_steps is not None else preset.get("num_steps", 5))
        self.max_number = int(max_number if max_number is not None else preset.get("max_number", 40))
        self.ops: List[str] = list(preset.get("ops", ["+", "-", "*"]))
        self.augment = augment

        # Каждый шаг: (a, op, b, shown_value, correct_value)
        self._steps: List[Tuple[int, str, int, int, int]] = []
        self._error_index: int = 0
        self._build_steps()

        section = PROMPT_TEMPLATES["find_the_error"]
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
        return a * b

    def _build_steps(self):
        self._steps = []
        for _ in range(max(2, self.num_steps)):
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
        section = PROMPT_TEMPLATES["find_the_error"]
        for i, (a, op, b, shown, correct) in enumerate(self._steps, start=1):
            if shown != correct:
                self.solution_steps.append(
                    get_template(section, "step_check", self.language, augment=False,
                                 n=i, a=a, op=op, b=b, shown=shown, correct=correct)
                )
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, n=self._error_index)
        )
        self.final_answer = str(self._error_index)

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
