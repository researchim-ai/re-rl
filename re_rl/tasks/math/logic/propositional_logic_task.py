"""PropositionalLogicTask — является ли булева формула тавтологией.

Генерирует формулу над несколькими переменными и определяет, истинна ли она
при всех означиваниях (тавтология). Проверка выполняется через z3: формула —
тавтология тогда и только тогда, когда её отрицание невыполнимо (UNSAT).

Ответ — ``YES`` / ``NO`` (в решении также принимаются синонимы да/нет/true/false).
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import z3

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class PropositionalLogicTask(BaseMathTask):
    """Проверка формулы на тавтологичность (z3)."""

    TASK_TYPE = "propositional_logic"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_vars": 2, "depth": 1},
        2: {"num_vars": 2, "depth": 2},
        3: {"num_vars": 2, "depth": 2},
        4: {"num_vars": 3, "depth": 2},
        5: {"num_vars": 3, "depth": 3},
        6: {"num_vars": 3, "depth": 3},
        7: {"num_vars": 3, "depth": 4},
        8: {"num_vars": 4, "depth": 4},
        9: {"num_vars": 4, "depth": 5},
        10: {"num_vars": 4, "depth": 5},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_vars: Optional[int] = None,
        depth: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_vars = int(num_vars if num_vars is not None else preset.get("num_vars", 3))
        self.depth = int(depth if depth is not None else preset.get("depth", 3))
        self.augment = augment

        self._var_names = ["p", "q", "r", "s"][: max(1, min(4, self.num_vars))]
        self._zvars = {n: z3.Bool(n) for n in self._var_names}

        formula, formula_str = self._build_formula()
        self._formula_str = formula_str
        self._is_tautology = self._check_tautology(formula)

        description = get_template(
            PROMPT_TEMPLATES["propositional_logic"],
            "problem",
            language,
            augment=augment,
            formula=formula_str,
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _build_expr(self, depth: int) -> Tuple[Any, str]:
        if depth <= 0 or random.random() < 0.3:
            name = random.choice(self._var_names)
            return self._zvars[name], name

        op = random.choice(["not", "and", "or", "implies"])
        if op == "not":
            e, s = self._build_expr(depth - 1)
            return z3.Not(e), f"¬{s}" if s in self._var_names else f"¬({s})"

        left, ls = self._build_expr(depth - 1)
        right, rs = self._build_expr(depth - 1)
        if op == "and":
            return z3.And(left, right), f"({ls} ∧ {rs})"
        if op == "or":
            return z3.Or(left, right), f"({ls} ∨ {rs})"
        return z3.Implies(left, right), f"({ls} → {rs})"

    def _build_formula(self) -> Tuple[Any, str]:
        base, base_str = self._build_expr(self.depth)
        # ~60% случаев строим формулу с известным вердиктом для баланса классов.
        if random.random() < 0.6:
            template = random.choice(["excluded_middle", "identity", "contradiction"])
            if template == "excluded_middle":  # всегда истинно (YES)
                return z3.Or(base, z3.Not(base)), f"({base_str} ∨ ¬({base_str}))"
            if template == "identity":  # всегда истинно (YES)
                return z3.Implies(base, base), f"({base_str} → {base_str})"
            # contradiction: (A ∧ ¬A) — никогда не тавтология (NO)
            return z3.And(base, z3.Not(base)), f"({base_str} ∧ ¬({base_str}))"
        return base, base_str

    @staticmethod
    def _check_tautology(formula: Any) -> bool:
        solver = z3.Solver()
        solver.add(z3.Not(formula))
        return solver.check() == z3.unsat

    def solve(self):
        section = PROMPT_TEMPLATES["propositional_logic"]
        answer = "YES" if self._is_tautology else "NO"
        self.solution_steps.append(get_template(section, "step_negate", self.language, augment=False))
        verdict_ru = "является" if self._is_tautology else "не является"
        verdict_en = "is" if self._is_tautology else "is not"
        verdict = verdict_ru if self.language == "ru" else verdict_en
        self.solution_steps.append(
            get_template(section, "step_result", self.language, augment=False, verdict=verdict, answer=answer)
        )
        self.final_answer = answer

    def verify(self, prediction: str) -> float:
        """Сравнение вердикта; принимает синонимы да/нет/true/false."""
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()

        _, answer = extract_reasoning_and_answer(prediction)
        text = (answer or prediction).strip().lower().strip(".!? ")

        # Точное совпадение короткого ответа.
        exact_yes = {"yes", "да", "true", "y", "1"}
        exact_no = {"no", "нет", "false", "n", "0"}
        if text in exact_yes:
            pred = "YES"
        elif text in exact_no:
            pred = "NO"
        else:
            # Поиск по ключевым словам (отрицание приоритетнее).
            import re as _re
            has_no = bool(_re.search(r"\b(no|нет|false|не\s+тавтолог\w*)\b", text))
            has_yes = bool(_re.search(r"\b(yes|да|true|тавтолог\w*)\b", text))
            if has_no:
                pred = "NO"
            elif has_yes:
                pred = "YES"
            else:
                return 0.0
        return 1.0 if pred == self.final_answer else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "PropositionalLogicTask":
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
