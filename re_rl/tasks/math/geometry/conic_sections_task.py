"""ConicSectionsTask — распознавание кривой второго порядка по уравнению.

Классификация по коэффициентам при x² и y²:
- ровно один квадрат → парабола;
- одинаковые коэффициенты одного знака → окружность;
- разные коэффициенты одного знака → эллипс;
- коэффициенты разных знаков → гипербола.
Проверка принимает синонимы термина на русском и английском.
"""

import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


_SYNONYMS = {
    "circle": ["circle", "окружность", "круг"],
    "ellipse": ["ellipse", "эллипс"],
    "hyperbola": ["hyperbola", "гипербола"],
    "parabola": ["parabola", "парабола"],
}
_RU = {"circle": "окружность", "ellipse": "эллипс", "hyperbola": "гипербола", "parabola": "парабола"}


class ConicSectionsTask(BaseMathTask):
    """Определить тип коники по уравнению (проверка по синонимам)."""

    TASK_TYPE = "conic_sections"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"coef": 4}, 2: {"coef": 5}, 3: {"coef": 6}, 4: {"coef": 7}, 5: {"coef": 8},
        6: {"coef": 9}, 7: {"coef": 10}, 8: {"coef": 12}, 9: {"coef": 14}, 10: {"coef": 16},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        coef: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.coef = int(coef if coef is not None else preset.get("coef", 8))
        self.augment = augment

        self._build()
        description = get_template(
            PROMPT_TEMPLATES["conic_sections"], "problem", language,
            augment=augment, equation=self._equation,
        )
        super().__init__(
            description=description, language=language, detail_level=detail_level,
            output_format=output_format, reasoning_mode=reasoning_mode,
        )

    def _nz(self, lo: int, hi: int) -> int:
        v = 0
        while v == 0:
            v = random.randint(lo, hi)
        return v

    def _build(self):
        c = self.coef
        kind = random.choice(["circle", "ellipse", "hyperbola", "parabola"])
        if kind == "circle":
            a = self._nz(1, c)
            A = C = a
        elif kind == "ellipse":
            A = self._nz(1, c)
            C = self._nz(1, c)
            while C == A:
                C = self._nz(1, c)
            if random.random() < 0.5:  # оба одного знака (отрицательные)
                A, C = -A, -C
        elif kind == "hyperbola":
            A = self._nz(1, c)
            C = -self._nz(1, c)
        else:  # parabola: ровно один квадрат
            if random.random() < 0.5:
                A, C = self._nz(1, c), 0
                lin = f" + {self._nz(1, c)}y"
            else:
                A, C = 0, self._nz(1, c)
                lin = f" + {self._nz(1, c)}x"
        self._kind = kind

        parts = []
        if A != 0:
            parts.append(f"{A}x^2")
        if C != 0:
            parts.append(f"{C}y^2")
        body = " + ".join(parts).replace("+ -", "- ")
        if kind == "parabola":
            body += lin
        f = self._nz(-c, c)
        rhs = -f
        self._equation = f"{body} + {f} = 0".replace("+ -", "- ")

        self.final_kind = kind

    def solve(self):
        section = PROMPT_TEMPLATES["conic_sections"]
        self.solution_steps.append(get_template(section, "step_setup", self.language, augment=False))
        word = _RU[self._kind] if self.language == "ru" else self._kind
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, result=word)
        )
        self.final_answer = word

    def verify(self, prediction: str) -> float:
        from re_rl.tasks.math._verify_utils import extract_answer_text

        if self.final_answer is None:
            self.solve()
        text = extract_answer_text(prediction).strip().lower()
        for syn in _SYNONYMS[self._kind]:
            if syn in text:
                # Убеждаемся, что не совпал синоним другого типа раньше.
                return 1.0
        return 0.0

    @classmethod
    def generate_random_task(
        cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
        reasoning_mode: bool = False, augment: bool = True, **kwargs,
    ) -> "ConicSectionsTask":
        task = cls(
            language=language, detail_level=detail_level, difficulty=difficulty,
            reasoning_mode=reasoning_mode, augment=augment, **kwargs,
        )
        task.solve()
        return task
