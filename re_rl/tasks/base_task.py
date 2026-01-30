# re_rl/tasks/base_task.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any, ClassVar, Dict, Optional, Type, TypeVar, Literal

from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.registry import registry


# Поддерживаемые форматы вывода математических выражений
OutputFormat = Literal["text", "latex"]


# =============================================================================
# Утилиты для форматирования reasoning-вывода
# =============================================================================

def format_reasoning_output(
    thinking_steps: List[str],
    answer: str,
    reasoning_mode: bool = False,
    language: str = "ru"
) -> str:
    """
    Форматирует вывод решения.
    
    Args:
        thinking_steps: Шаги рассуждения
        answer: Финальный ответ
        reasoning_mode: Если True — оборачивает в <think>/<answer> теги
        language: Язык для префикса ответа
    
    Returns:
        Отформатированная строка решения
    """
    steps_text = "\n".join(thinking_steps)
    
    if reasoning_mode:
        return f"<think>\n{steps_text}\n</think>\n<answer>{answer}</answer>"
    else:
        answer_prefix = "Ответ:" if language == "ru" else "Answer:"
        return f"{steps_text}\n\n{answer_prefix} {answer}"


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
    output_format: OutputFormat = "text"  # "text" или "latex"
    reasoning_mode: bool = False  # Если True — выводит <think>/<answer> теги

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
    # Методы для структурированного reasoning-решения
    # ------------------------------------------------------------------
    
    def add_given(self, variables: Dict[str, Any], units: Optional[Dict[str, str]] = None) -> None:
        """
        Добавляет блок "Дано" в решение (только для reasoning_mode).
        
        Args:
            variables: Словарь {имя: значение}
            units: Словарь {имя: единица измерения}
        
        Пример:
            self.add_given({"v₀": 14, "g": 9.81}, {"v₀": "м/с", "g": "м/с²"})
        """
        if not self.reasoning_mode:
            return
        
        units = units or {}
        given_text = "Дано:" if self.language == "ru" else "Given:"
        lines = [given_text]
        for name, value in variables.items():
            unit = units.get(name, "")
            if unit:
                lines.append(f"  {name} = {value} {unit}")
            else:
                lines.append(f"  {name} = {value}")
        self.solution_steps.append("\n".join(lines))
    
    def add_find(self, target: str, description: str = "") -> None:
        """
        Добавляет блок "Найти" в решение (только для reasoning_mode).
        
        Args:
            target: Что нужно найти (например, "h")
            description: Описание (например, "максимальная высота")
        """
        if not self.reasoning_mode:
            return
        
        find_text = "Найти:" if self.language == "ru" else "Find:"
        if description:
            self.solution_steps.append(f"{find_text} {target} — {description}")
        else:
            self.solution_steps.append(f"{find_text} {target}")
    
    def add_analysis(self, text: str) -> None:
        """
        Добавляет анализ/рассуждение (только для reasoning_mode).
        
        Args:
            text: Текст анализа
        """
        if not self.reasoning_mode:
            return
        self.solution_steps.append(text)
    
    def add_formula(self, formula: str, name: str = "") -> None:
        """
        Добавляет формулу. ВСЕГДА добавляется (и в reasoning, и в обычном режиме).
        
        Args:
            formula: Формула (например, "h = v₀²/(2g)")
            name: Название формулы (например, "Закон сохранения энергии")
        """
        formula_label = "Формула:" if self.language == "ru" else "Formula:"
        if name:
            self.solution_steps.append(f"{formula_label} {formula}  ({name})")
        else:
            self.solution_steps.append(f"{formula_label} {formula}")
    
    def add_substitution(self, expression: str) -> None:
        """
        Добавляет подстановку значений в формулу.
        
        Args:
            expression: Выражение с подставленными значениями
        """
        subst_label = "Подстановка:" if self.language == "ru" else "Substitution:"
        self.solution_steps.append(f"{subst_label} {expression}")
    
    def add_calculation(self, expression: str, result: Any, unit: str = "") -> None:
        """
        Добавляет вычисление.
        
        Args:
            expression: Промежуточное выражение
            result: Результат вычисления
            unit: Единица измерения
        """
        calc_label = "Вычисление:" if self.language == "ru" else "Calculation:"
        if unit:
            self.solution_steps.append(f"{calc_label} {expression} = {result} {unit}")
        else:
            self.solution_steps.append(f"{calc_label} {expression} = {result}")
    
    def add_dimension_check(self, check: str) -> None:
        """
        Добавляет проверку размерности (только для reasoning_mode).
        
        Args:
            check: Проверка размерности (например, "[м/с]²/[м/с²] = [м] ✓")
        """
        if not self.reasoning_mode:
            return
        check_label = "Проверка размерности:" if self.language == "ru" else "Dimension check:"
        self.solution_steps.append(f"{check_label} {check}")
    
    def add_verification(self, text: str) -> None:
        """
        Добавляет проверку ответа (только для reasoning_mode).
        
        Args:
            text: Текст проверки
        """
        if not self.reasoning_mode:
            return
        verify_label = "Проверка:" if self.language == "ru" else "Verification:"
        self.solution_steps.append(f"{verify_label} {text}")
    
    def format_final_output(self) -> str:
        """
        Форматирует финальный вывод решения с учётом reasoning_mode.
        
        Returns:
            Отформатированная строка решения
        """
        return format_reasoning_output(
            thinking_steps=self.solution_steps,
            answer=str(self.final_answer),
            reasoning_mode=self.reasoning_mode,
            language=self.language
        )

    # ------------------------------------------------------------------
    # task_type уже определяется метаклассом, поэтому заглушка не нужна
    # ------------------------------------------------------------------
