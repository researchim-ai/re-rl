# re_rl/tasks/base_task.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any, ClassVar

from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.registry import registry


class TaskMeta(type):
    """Метакласс, автоматически добавляющий Task-классы в общий реестр."""

    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]):  # type: ignore[name-defined]
        super().__init__(name, bases, namespace)

        # Пропускаем абстрактные базовые классы
        if name in {"BaseTask", "BaseMathTask"}:
            return

        # Определяем task_type. По умолчанию преобразуем CamelCase в snake_case
        def _camel_to_snake(s: str) -> str:
            import re
            return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()

        default_type = _camel_to_snake(name.replace("Task", ""))
        task_type: str = getattr(cls, "TASK_TYPE", default_type)
        registry[task_type] = cls  # регистрация

        # Сохраняем как class attr для удобства
        cls.TASK_TYPE = task_type  # type: ignore[attr-defined]


@dataclass
class BaseTask(metaclass=TaskMeta):
    """Базовый класс для всех типов задач (не только математических)."""

    description: str
    language: str = "en"

    # Итоги решения
    solution_steps: List[str] = field(default_factory=list, init=False)
    explanation_steps: List[str] = field(default_factory=list, init=False)
    validation_steps: List[str] = field(default_factory=list, init=False)
    final_answer: Any = field(default=None, init=False)

    # Должен быть переопределён автоматически TaskMeta, но объявляем для type-checker
    TASK_TYPE: ClassVar[str]

    # ---------------------------------------------------------------------
    # Методы, общие для всех задач
    # ---------------------------------------------------------------------

    def generate_prompt(self) -> str:
        """Шаблонный промпт, может быть переопределён."""
        default = PROMPT_TEMPLATES["default"]["prompt"]
        lang = self.language.lower()
        prompt_template = default.get(lang, default["en"])
        return prompt_template.format(problem=self.description)

    # Конкретная задача обязана реализовать solve()
    def solve(self):  # noqa: D401  (human-readable comment style)
        """Выполняет пошаговое решение, заполняя solution_steps и final_answer."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Унифицированный вывод результата
    # ------------------------------------------------------------------
    def get_result(self) -> dict[str, Any]:
        """Возвращает структуру результата для обучения/оценки."""
        if (not self.solution_steps) or (self.final_answer is None):
            self.solve()

        result: dict[str, Any] = {
            "task_type": self.TASK_TYPE,
            "problem": self.description,
            "language": self.language,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer,
        }

        if self.explanation_steps:
            result["explanations"] = self.explanation_steps
        if self.validation_steps:
            result["validations"] = self.validation_steps

        return result

# -----------------------------------------------------------------------------
# Базовый математический таск
# -----------------------------------------------------------------------------


@dataclass
class BaseMathTask(BaseTask):
    """Добавляет `detail_level` и общие утилиты для математических задач."""

    detail_level: int = 3

    # ------------------------------------------------------------------
    # Утилиты, специфичные для математики
    # ------------------------------------------------------------------

    def generate_prompt(self) -> str:  # type: ignore[override]
        default = PROMPT_TEMPLATES["default"]["prompt"]
        prompt_template = default.get(self.language, default["en"])
        return prompt_template.format(problem=self.description)

    def add_solution_step(
        self,
        step: str,
        explanation: str | None = None,
        validation: str | None = None,
    ) -> None:
        self.solution_steps.append(step)
        if explanation:
            self.explanation_steps.append(explanation)
        if validation:
            self.validation_steps.append(validation)

    def validate_step(self, step_index: int) -> bool:
        """
        Проверяет корректность шага решения.
        """
        if 0 <= step_index < len(self.solution_steps):
            return True
        return False

    def get_step_explanation(self, step_index: int) -> str:
        """
        Возвращает объяснение для конкретного шага.
        """
        if 0 <= step_index < len(self.explanation_steps):
            return self.explanation_steps[step_index]
        return ""

    def get_step_validation(self, step_index: int) -> str:
        """
        Возвращает валидацию для конкретного шага.
        """
        if 0 <= step_index < len(self.validation_steps):
            return self.validation_steps[step_index]
        return ""

    def generate_latex_solution(self) -> str:
        import sympy as sp
        latex_steps = []
        for i, step in enumerate(self.solution_steps):
            try:
                expr = sp.sympify(step)
                latex_steps.append(sp.latex(expr))
                if self.get_step_explanation(i):
                    latex_steps.append(r"\text{" + self.get_step_explanation(i) + "}")
                if self.get_step_validation(i):
                    latex_steps.append(r"\text{" + self.get_step_validation(i) + "}")
            except Exception:
                safe_step = step.replace("_", r"\_").replace("%", r"\%")
                latex_steps.append(r"\text{" + safe_step + "}")
        return r"\begin{align*}" + " \\\\\n".join(latex_steps) + r"\end{align*}"

    # ------------------------------------------------------------------
    # task_type уже определяется метаклассом, поэтому заглушка не нужна
    # ------------------------------------------------------------------
