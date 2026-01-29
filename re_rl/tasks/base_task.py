# re_rl/tasks/base_task.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any, ClassVar, Dict, Optional, Type, TypeVar

from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.registry import registry


# Типовая переменная для from_difficulty
T = TypeVar('T', bound='BaseTask')


class DifficultyMixin:
    """
    Миксин для унифицированной системы сложности задач.
    
    Классы-наследники должны определить:
    - DIFFICULTY_PRESETS: Dict[int, Dict[str, Any]] — пресеты параметров для уровней 1-10
    
    Пример использования:
        class MyTask(DifficultyMixin, BaseMathTask):
            DIFFICULTY_PRESETS = {
                1: {"param1": 1, "param2": 5},
                5: {"param1": 5, "param2": 25},
                10: {"param1": 10, "param2": 100},
            }
            
        task = MyTask.from_difficulty(7, language="ru")
    """
    
    # Переопределяется в каждом классе-наследнике
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {}
    
    @classmethod
    def from_difficulty(
        cls: Type[T],
        difficulty: int,
        language: str = "ru",
        detail_level: int = 3,
        **overrides
    ) -> T:
        """
        Создаёт задачу с заданным уровнем сложности.
        
        Args:
            difficulty: Уровень сложности (1-10)
            language: Язык ("ru" или "en")
            detail_level: Уровень детализации решения
            **overrides: Параметры для переопределения пресета
            
        Returns:
            Экземпляр задачи с настроенными параметрами
        """
        params = cls._interpolate_difficulty(difficulty)
        params.update(overrides)
        
        # Добавляем language и detail_level
        params['language'] = language
        if hasattr(cls, 'detail_level') or 'detail_level' in cls.__init__.__code__.co_varnames:
            params['detail_level'] = detail_level
            
        return cls(**params)
    
    @classmethod
    def _interpolate_difficulty(cls, difficulty: int) -> Dict[str, Any]:
        """
        Интерполирует параметры между пресетами сложности.
        
        Если точного пресета нет, интерполирует между ближайшими.
        """
        presets = cls.DIFFICULTY_PRESETS
        if not presets:
            return {}
        
        difficulty = max(1, min(10, difficulty))  # Ограничиваем 1-10
        
        # Точное совпадение
        if difficulty in presets:
            return presets[difficulty].copy()
        
        # Находим ближайшие пресеты
        lower_levels = [l for l in presets.keys() if l < difficulty]
        upper_levels = [l for l in presets.keys() if l > difficulty]
        
        if not lower_levels:
            return presets[min(presets.keys())].copy()
        if not upper_levels:
            return presets[max(presets.keys())].copy()
        
        lower = max(lower_levels)
        upper = min(upper_levels)
        
        # Интерполяция
        ratio = (difficulty - lower) / (upper - lower)
        lower_params = presets[lower]
        upper_params = presets[upper]
        
        result = {}
        for key in lower_params:
            lower_val = lower_params[key]
            upper_val = upper_params.get(key, lower_val)
            
            if isinstance(lower_val, (int, float)) and isinstance(upper_val, (int, float)):
                # Числовая интерполяция
                interpolated = lower_val + (upper_val - lower_val) * ratio
                result[key] = int(interpolated) if isinstance(lower_val, int) else interpolated
            else:
                # Для нечисловых параметров выбираем ближайший
                result[key] = lower_val if ratio < 0.5 else upper_val
        
        # Добавляем параметры, которые есть только в upper
        for key in upper_params:
            if key not in result:
                result[key] = upper_params[key]
        
        return result
    
    @classmethod
    def get_difficulty_range(cls) -> tuple[int, int]:
        """Возвращает диапазон поддерживаемых уровней сложности."""
        if not cls.DIFFICULTY_PRESETS:
            return (1, 10)
        return (min(cls.DIFFICULTY_PRESETS.keys()), max(cls.DIFFICULTY_PRESETS.keys()))


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
class BaseTask(DifficultyMixin, metaclass=TaskMeta):
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
