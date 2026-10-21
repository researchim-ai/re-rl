"""BaseConversionTask — перевод чисел между системами счисления и битовые операции.

Подтипы:
- ``convert``: перевести число из основания b1 в основание b2.
- ``bitwise``: вычислить побитовую операцию (AND/OR/XOR/сдвиг), ответ в 10-й системе.
"""

import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template

_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def to_base(value: int, base: int) -> str:
    if value == 0:
        return "0"
    neg = value < 0
    value = abs(value)
    out = []
    while value:
        out.append(_DIGITS[value % base])
        value //= base
    if neg:
        out.append("-")
    return "".join(reversed(out))


class BaseConversionTask(BaseMathTask):
    """Системы счисления и битовые операции."""

    TASK_TYPE = "base_conversion"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_value": 15, "subtype": "convert", "bases": [2]},
        2: {"max_value": 31, "subtype": "convert", "bases": [2]},
        3: {"max_value": 63, "subtype": "convert", "bases": [2, 8]},
        4: {"max_value": 255, "subtype": "convert", "bases": [2, 8, 16]},
        5: {"max_value": 255, "subtype": "bitwise", "bases": [2, 8, 16]},
        6: {"max_value": 511, "subtype": "bitwise", "bases": [2, 8, 16]},
        7: {"max_value": 1023, "subtype": "convert", "bases": [2, 8, 16]},
        8: {"max_value": 2047, "subtype": "bitwise", "bases": [2, 8, 16]},
        9: {"max_value": 4095, "subtype": "convert", "bases": [2, 8, 16]},
        10: {"max_value": 8191, "subtype": "bitwise", "bases": [2, 8, 16]},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        subtype: Optional[str] = None,
        max_value: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or preset.get("subtype", "convert")
        self.max_value = int(max_value if max_value is not None else preset.get("max_value", 255))
        self._bases = list(preset.get("bases", [2, 8, 16]))
        self.augment = augment

        self.target_base = 10
        self._value = 0

        if self.subtype == "convert":
            self._value = random.randint(1, self.max_value)
            b1 = random.choice([10] + self._bases)
            b2 = random.choice([b for b in ([10] + self._bases) if b != b1])
            self.target_base = b2
            number_repr = to_base(self._value, b1)
            description = get_template(
                PROMPT_TEMPLATES["base_conversion"], "convert_problem", language,
                augment=augment, number=number_repr, b1=b1, b2=b2,
            )
        else:
            a = random.randint(1, self.max_value)
            b = random.randint(1, self.max_value)
            op = random.choice(["AND", "OR", "XOR", "<<", ">>"])
            if op == "AND":
                self._value = a & b
                expr = f"{a} AND {b}"
            elif op == "OR":
                self._value = a | b
                expr = f"{a} OR {b}"
            elif op == "XOR":
                self._value = a ^ b
                expr = f"{a} XOR {b}"
            elif op == "<<":
                shift = random.randint(1, 3)
                self._value = a << shift
                expr = f"{a} << {shift}"
            else:
                shift = random.randint(1, 3)
                self._value = a >> shift
                expr = f"{a} >> {shift}"
            self.target_base = 10
            description = get_template(
                PROMPT_TEMPLATES["base_conversion"], "bitwise_problem", language,
                augment=augment, expr=expr,
            )

        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def solve(self):
        section = PROMPT_TEMPLATES["base_conversion"]
        result = to_base(self._value, self.target_base)
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=result)
        )
        self.final_answer = result

    def verify(self, prediction: str) -> float:
        """Сравнение по значению (учитывая целевую систему счисления)."""
        import re
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()
        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip()

        # Извлекаем токен-число в целевой системе (возможен префикс 0x/0b/0o).
        token = text.split()[-1] if text.split() else text
        token = token.strip().rstrip(".").lstrip("+")
        token = re.sub(r"^0[xbo]", "", token, flags=re.IGNORECASE)
        try:
            pred_value = int(token, self.target_base)
        except ValueError:
            # Иногда модель отвечает в десятичной — примем и это.
            try:
                pred_value = int(re.sub(r"[^0-9-]", "", token) or "x", 10)
            except ValueError:
                return 0.0
        return 1.0 if pred_value == self._value else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "BaseConversionTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
