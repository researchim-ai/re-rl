# re_rl/tasks/physics/mechanics/kinematics_task.py

"""
KinematicsTask — задачи по кинематике.

Типы задач:
- uniform_motion: равномерное движение
- find_velocity: найти скорость
- accelerated_distance: равноускоренное движение (путь)
- accelerated_velocity: равноускоренное движение (скорость)
- projectile_max_height: максимальная высота броска
- projectile_range: дальность полёта
- circular_velocity: скорость при круговом движении
- circular_acceleration: центростремительное ускорение
"""

import random
import math
from typing import Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.units import format_with_units
from re_rl.tasks.formatting import MathFormatter


class KinematicsTask(BaseMathTask):
    """Генератор задач по кинематике."""
    
    TASK_TYPES = [
        "uniform_motion", "find_velocity", "accelerated_distance",
        "accelerated_velocity", "projectile_max_height", "projectile_range",
        "circular_velocity", "circular_acceleration"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_v": 10, "max_t": 10, "max_a": 2, "simple": True},
        2: {"max_v": 20, "max_t": 15, "max_a": 3, "simple": True},
        3: {"max_v": 30, "max_t": 20, "max_a": 5, "simple": True},
        4: {"max_v": 50, "max_t": 30, "max_a": 5, "simple": False},
        5: {"max_v": 50, "max_t": 30, "max_a": 10, "simple": False},
        6: {"max_v": 100, "max_t": 60, "max_a": 10, "simple": False},
        7: {"max_v": 100, "max_t": 60, "max_a": 15, "simple": False},
        8: {"max_v": 200, "max_t": 100, "max_a": 15, "simple": False},
        9: {"max_v": 200, "max_t": 100, "max_a": 20, "simple": False},
        10: {"max_v": 300, "max_t": 120, "max_a": 20, "simple": False},
    }
    
    def __init__(
        self,
        task_type: str = "uniform_motion",
        v: float = None,
        v0: float = None,
        t: float = None,
        s: float = None,
        a: float = None,
        r: float = None,
        T: float = None,
        angle: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.language = language
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        self.g = get_constant("g")
        
        # Параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        max_v = preset.get("max_v", 50)
        max_t = preset.get("max_t", 30)
        max_a = preset.get("max_a", 10)
        
        # Генерируем параметры
        self.v = v if v is not None else random.randint(5, max_v)
        self.v0 = v0 if v0 is not None else random.randint(0, max_v // 2)
        self.t = t if t is not None else random.randint(2, max_t)
        self.s = s if s is not None else random.randint(10, max_v * max_t)
        self.a = a if a is not None else random.randint(1, max_a)
        self.r = r if r is not None else random.randint(1, 50)
        self.T = T if T is not None else random.randint(1, 20)
        self.angle = angle if angle is not None else random.choice([30, 45, 60])
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("kinematics", {}).get("problem", {})
        
        if self.task_type == "uniform_motion":
            template = templates.get("uniform_motion", {}).get(self.language, "")
            return template.format(v=self.v, t=self.t)
        
        elif self.task_type == "find_velocity":
            template = templates.get("find_velocity", {}).get(self.language, "")
            return template.format(s=self.s, t=self.t)
        
        elif self.task_type == "accelerated_distance":
            template = templates.get("accelerated_distance", {}).get(self.language, "")
            return template.format(a=self.a, t=self.t)
        
        elif self.task_type == "accelerated_velocity":
            template = templates.get("accelerated_velocity", {}).get(self.language, "")
            return template.format(v0=self.v0, a=self.a, t=self.t)
        
        elif self.task_type == "projectile_max_height":
            template = templates.get("projectile_max_height", {}).get(self.language, "")
            return template.format(v0=self.v0 or self.v, g=self.g)
        
        elif self.task_type == "projectile_range":
            template = templates.get("projectile_range", {}).get(self.language, "")
            return template.format(angle=self.angle, v0=self.v, g=self.g)
        
        elif self.task_type == "circular_velocity":
            template = templates.get("circular_velocity", {}).get(self.language, "")
            return template.format(r=self.r, T=self.T)
        
        elif self.task_type == "circular_acceleration":
            template = templates.get("circular_acceleration", {}).get(self.language, "")
            return template.format(r=self.r, v=self.v)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("kinematics", {}).get("steps", {})
        formulas = PROMPT_TEMPLATES.get("kinematics", {}).get("formulas", {})
        
        if self.task_type == "uniform_motion":
            self._solve_uniform_motion(templates, formulas)
        elif self.task_type == "find_velocity":
            self._solve_find_velocity(templates, formulas)
        elif self.task_type == "accelerated_distance":
            self._solve_accelerated_distance(templates, formulas)
        elif self.task_type == "accelerated_velocity":
            self._solve_accelerated_velocity(templates, formulas)
        elif self.task_type == "projectile_max_height":
            self._solve_projectile_max_height(templates, formulas)
        elif self.task_type == "projectile_range":
            self._solve_projectile_range(templates, formulas)
        elif self.task_type == "circular_velocity":
            self._solve_circular_velocity(templates, formulas)
        elif self.task_type == "circular_acceleration":
            self._solve_circular_acceleration(templates, formulas)
        
        # НЕ обрезаем шаги — в reasoning_mode нужны все шаги
        # detail_level теперь контролирует уровень детализации, а не обрезку
    
    def _format_value(self, value, unit):
        """Форматирует значение с единицей измерения."""
        if self._output_format == "latex":
            return MathFormatter.format_physics_value(value, unit, "latex")
        return format_with_units(value, unit, self.language)
    
    def _format_formula(self, formula_text, formula_latex):
        """Форматирует формулу в зависимости от формата."""
        if self._output_format == "latex":
            return f"${formula_latex}$"
        return formula_text
    
    def _solve_uniform_motion(self, templates, formulas):
        """s = v * t"""
        s = self.v * self.t
        
        # Reasoning mode: добавляем "Дано" и анализ
        if self.reasoning_mode:
            self.add_given(
                {"v": self.v, "t": self.t},
                {"v": "м/с", "t": "с"}
            )
            self.add_find("s", "пройденный путь" if self.language == "ru" else "distance traveled")
            self.add_analysis(
                "Равномерное движение — скорость постоянна." if self.language == "ru" 
                else "Uniform motion — velocity is constant."
            )
        
        # Формула (ВСЕГДА)
        self.add_formula("s = v × t")
        
        # Подстановка
        self.add_substitution(f"s = {self.v} × {self.t}")
        
        # Вычисление
        self.add_calculation(f"{self.v} × {self.t}", s, "м")
        
        # Проверка размерности (только reasoning mode)
        if self.reasoning_mode:
            self.add_dimension_check("[м/с] × [с] = [м] ✓")
        
        self.final_answer = self._format_value(s, "m")
    
    def _solve_find_velocity(self, templates, formulas):
        """v = s / t"""
        v = self.s / self.t
        
        if self.reasoning_mode:
            self.add_given(
                {"s": self.s, "t": self.t},
                {"s": "м", "t": "с"}
            )
            self.add_find("v", "скорость" if self.language == "ru" else "velocity")
        
        self.add_formula("v = s/t")
        self.add_substitution(f"v = {self.s} / {self.t}")
        self.add_calculation(f"{self.s}/{self.t}", round(v, 4), "м/с")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м]/[с] = [м/с] ✓")
        
        self.final_answer = format_with_units(v, "m/s", self.language)
    
    def _solve_accelerated_distance(self, templates, formulas):
        """s = at²/2 (из покоя)"""
        s = self.a * self.t ** 2 / 2
        
        if self.reasoning_mode:
            self.add_given(
                {"a": self.a, "t": self.t, "v₀": 0},
                {"a": "м/с²", "t": "с", "v₀": "м/с"}
            )
            self.add_find("s", "пройденный путь" if self.language == "ru" else "distance")
            self.add_analysis(
                "Движение из состояния покоя (v₀ = 0) с постоянным ускорением."
                if self.language == "ru" else
                "Motion from rest (v₀ = 0) with constant acceleration."
            )
        
        self.add_formula("s = v₀t + at²/2 = at²/2")
        self.add_substitution(f"s = {self.a} × {self.t}² / 2")
        self.add_calculation(f"{self.a} × {self.t**2} / 2", round(s, 4), "м")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м/с²] × [с²] = [м] ✓")
        
        self.final_answer = format_with_units(s, "m", self.language)
    
    def _solve_accelerated_velocity(self, templates, formulas):
        """v = v0 + at"""
        v = self.v0 + self.a * self.t
        
        if self.reasoning_mode:
            self.add_given(
                {"v₀": self.v0, "a": self.a, "t": self.t},
                {"v₀": "м/с", "a": "м/с²", "t": "с"}
            )
            self.add_find("v", "конечная скорость" if self.language == "ru" else "final velocity")
        
        self.add_formula("v = v₀ + at")
        self.add_substitution(f"v = {self.v0} + {self.a} × {self.t}")
        self.add_calculation(f"{self.v0} + {self.a * self.t}", round(v, 4), "м/с")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м/с] + [м/с²]×[с] = [м/с] + [м/с] = [м/с] ✓")
        
        self.final_answer = format_with_units(v, "m/s", self.language)
    
    def _solve_projectile_max_height(self, templates, formulas):
        """h = v0² / (2g)"""
        v0 = self.v0 if self.v0 else self.v
        h = v0 ** 2 / (2 * self.g)
        
        # Reasoning mode: добавляем "Дано" и анализ
        if self.reasoning_mode:
            self.add_given(
                {"v₀": v0, "g": self.g},
                {"v₀": "м/с", "g": "м/с²"}
            )
            self.add_find("h", "максимальная высота подъёма" if self.language == "ru" else "maximum height")
            self.add_analysis(
                "На максимальной высоте скорость равна нулю (v = 0).\n"
                "Используем связь скорости и перемещения: v² = v₀² - 2gh"
                if self.language == "ru" else
                "At maximum height velocity equals zero (v = 0).\n"
                "Use velocity-displacement relation: v² = v₀² - 2gh"
            )
        
        # Формула (ВСЕГДА)
        self.add_formula("h = v₀²/(2g)")
        
        # Подстановка
        self.add_substitution(f"h = ({v0})²/(2 × {self.g})")
        
        # Вычисление
        v0_squared = v0 ** 2
        two_g = 2 * self.g
        self.add_calculation(f"{v0_squared}/{two_g:.2f}", round(h, 4), "м")
        
        # Проверка размерности (только reasoning mode)
        if self.reasoning_mode:
            self.add_dimension_check("[м/с]²/[м/с²] = [м²/с²]/[м/с²] = [м] ✓")
        
        self.final_answer = format_with_units(h, "m", self.language)
    
    def _solve_projectile_range(self, templates, formulas):
        """R = v0² sin(2θ) / g"""
        angle_rad = math.radians(2 * self.angle)
        R = self.v ** 2 * math.sin(angle_rad) / self.g
        
        if self.reasoning_mode:
            self.add_given(
                {"v₀": self.v, "θ": self.angle, "g": self.g},
                {"v₀": "м/с", "θ": "°", "g": "м/с²"}
            )
            self.add_find("R", "дальность полёта" if self.language == "ru" else "range")
            self.add_analysis(
                "Баллистическая задача. Дальность полёта максимальна при угле 45°."
                if self.language == "ru" else
                "Projectile motion problem. Maximum range is achieved at 45° angle."
            )
        
        self.add_formula("R = v₀² × sin(2θ) / g")
        self.add_substitution(f"R = {self.v}² × sin(2×{self.angle}°) / {self.g}")
        sin_2theta = round(math.sin(angle_rad), 4)
        self.solution_steps.append(f"sin(2×{self.angle}°) = sin({2*self.angle}°) = {sin_2theta}")
        self.add_calculation(f"{self.v**2} × {sin_2theta} / {self.g}", round(R, 4), "м")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м/с]² × [1] / [м/с²] = [м] ✓")
        
        self.final_answer = format_with_units(R, "m", self.language)
    
    def _solve_circular_velocity(self, templates, formulas):
        """v = 2πr / T"""
        v = 2 * math.pi * self.r / self.T
        
        if self.reasoning_mode:
            self.add_given(
                {"r": self.r, "T": self.T},
                {"r": "м", "T": "с"}
            )
            self.add_find("v", "линейная скорость" if self.language == "ru" else "linear velocity")
            self.add_analysis(
                "За один период T тело проходит длину окружности 2πr."
                if self.language == "ru" else
                "In one period T the body travels the circumference 2πr."
            )
        
        self.add_formula("v = 2πr/T")
        self.add_substitution(f"v = 2π × {self.r} / {self.T}")
        self.add_calculation(f"2 × 3.1416 × {self.r} / {self.T}", round(v, 4), "м/с")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м]/[с] = [м/с] ✓")
        
        self.final_answer = format_with_units(v, "m/s", self.language)
    
    def _solve_circular_acceleration(self, templates, formulas):
        """a = v² / r"""
        a = self.v ** 2 / self.r
        
        if self.reasoning_mode:
            self.add_given(
                {"v": self.v, "r": self.r},
                {"v": "м/с", "r": "м"}
            )
            self.add_find("a", "центростремительное ускорение" if self.language == "ru" else "centripetal acceleration")
            self.add_analysis(
                "При движении по окружности возникает центростремительное ускорение, направленное к центру."
                if self.language == "ru" else
                "Circular motion produces centripetal acceleration directed toward the center."
            )
        
        self.add_formula("a = v²/r")
        self.add_substitution(f"a = {self.v}² / {self.r}")
        self.add_calculation(f"{self.v**2}/{self.r}", round(a, 4), "м/с²")
        
        if self.reasoning_mode:
            self.add_dimension_check("[м/с]²/[м] = [м²/с²]/[м] = [м/с²] ✓")
        
        self.final_answer = format_with_units(a, "m/s^2", self.language)
    
    def get_task_type(self) -> str:
        return "kinematics"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format,
            reasoning_mode=reasoning_mode
        )
