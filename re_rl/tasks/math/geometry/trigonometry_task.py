# re_rl/tasks/trigonometry_task.py

"""
TrigonometryTask — тригонометрические задачи.

Поддерживаемые типы:
- basic_value: значения тригонометрических функций
- equation: тригонометрические уравнения
- identity: упрощение тождеств
- triangle_solve: решение треугольников
- inverse: обратные тригонометрические функции
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass
from fractions import Fraction

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class TrigonometryTask(BaseMathTask):
    """Тригонометрические задачи."""
    
    TASK_TYPES = [
        "basic_value", "equation", "identity", "triangle_solve", "inverse"
    ]
    
    # Стандартные углы в градусах и радианах
    STANDARD_ANGLES = [
        (0, "0"),
        (30, "π/6"),
        (45, "π/4"),
        (60, "π/3"),
        (90, "π/2"),
        (120, "2π/3"),
        (135, "3π/4"),
        (150, "5π/6"),
        (180, "π"),
        (210, "7π/6"),
        (225, "5π/4"),
        (240, "4π/3"),
        (270, "3π/2"),
        (300, "5π/3"),
        (315, "7π/4"),
        (330, "11π/6"),
        (360, "2π"),
    ]
    
    # Точные значения для стандартных углов
    EXACT_VALUES = {
        0: {"sin": "0", "cos": "1", "tan": "0"},
        30: {"sin": "1/2", "cos": "√3/2", "tan": "√3/3"},
        45: {"sin": "√2/2", "cos": "√2/2", "tan": "1"},
        60: {"sin": "√3/2", "cos": "1/2", "tan": "√3"},
        90: {"sin": "1", "cos": "0", "tan": "не определён"},
        120: {"sin": "√3/2", "cos": "-1/2", "tan": "-√3"},
        135: {"sin": "√2/2", "cos": "-√2/2", "tan": "-1"},
        150: {"sin": "1/2", "cos": "-√3/2", "tan": "-√3/3"},
        180: {"sin": "0", "cos": "-1", "tan": "0"},
        210: {"sin": "-1/2", "cos": "-√3/2", "tan": "√3/3"},
        225: {"sin": "-√2/2", "cos": "-√2/2", "tan": "1"},
        240: {"sin": "-√3/2", "cos": "-1/2", "tan": "√3"},
        270: {"sin": "-1", "cos": "0", "tan": "не определён"},
        300: {"sin": "-√3/2", "cos": "1/2", "tan": "-√3"},
        315: {"sin": "-√2/2", "cos": "√2/2", "tan": "-1"},
        330: {"sin": "-1/2", "cos": "√3/2", "tan": "-√3/3"},
        360: {"sin": "0", "cos": "1", "tan": "0"},
    }
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"complexity": 1},
        2: {"complexity": 1},
        3: {"complexity": 2},
        4: {"complexity": 2},
        5: {"complexity": 3},
        6: {"complexity": 3},
        7: {"complexity": 4},
        8: {"complexity": 4},
        9: {"complexity": 5},
        10: {"complexity": 5},
    }
    
    def __init__(
        self,
        task_type: str = "basic_value",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self.kwargs = kwargs
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.complexity = kwargs.get("complexity", preset.get("complexity", 2))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type == "basic_value":
            angle_deg, angle_rad = random.choice(self.STANDARD_ANGLES[:9])  # Первый квадрант + границы
            self.angle_deg = angle_deg
            self.angle_rad = angle_rad
            self.func = random.choice(["sin", "cos", "tan"])
            
            # Избегаем неопределённых значений
            if self.func == "tan" and angle_deg in [90, 270]:
                self.func = random.choice(["sin", "cos"])
        
        elif self.task_type == "equation":
            self._generate_equation_params()
        
        elif self.task_type == "identity":
            self._generate_identity_params()
        
        elif self.task_type == "triangle_solve":
            self._generate_triangle_params()
        
        elif self.task_type == "inverse":
            self._generate_inverse_params()
    
    def _generate_equation_params(self):
        """Генерирует параметры для тригонометрического уравнения."""
        equation_types = [
            ("sin(x) = {value}", "sin_eq"),
            ("cos(x) = {value}", "cos_eq"),
            ("2sin(x) - 1 = 0", "sin_half"),
            ("2cos(x) + 1 = 0", "cos_neg_half"),
            ("sin(2x) = 0", "sin_double"),
            ("tan(x) = 1", "tan_one"),
        ]
        
        self.eq_type = random.choice(equation_types[:self.complexity + 1])
        self.equation_template, self.eq_key = self.eq_type
        
        if "{value}" in self.equation_template:
            values = ["0", "1", "-1", "1/2", "-1/2", "√2/2", "-√2/2", "√3/2", "-√3/2"]
            self.value = random.choice(values[:self.complexity + 2])
            self.equation = self.equation_template.format(value=self.value)
        else:
            self.equation = self.equation_template
        
        self.interval = "[0, 2π]"
    
    def _generate_identity_params(self):
        """Генерирует параметры для тождества."""
        identities = [
            ("sin²(x) + cos²(x)", "1", "pythagorean"),
            ("1 - cos²(x)", "sin²(x)", "pythagorean_sin"),
            ("1 - sin²(x)", "cos²(x)", "pythagorean_cos"),
            ("sin(2x)", "2sin(x)cos(x)", "double_sin"),
            ("cos(2x)", "cos²(x) - sin²(x)", "double_cos"),
            ("tan(x) × cos(x)", "sin(x)", "tan_cos"),
            ("sin(x)/cos(x)", "tan(x)", "tan_def"),
        ]
        
        self.identity = random.choice(identities[:self.complexity + 2])
        self.expression, self.simplified, self.identity_name = self.identity
    
    def _generate_triangle_params(self):
        """Генерирует параметры для решения треугольника."""
        # Генерируем треугольник с известными элементами
        self.a = random.randint(3, 15)
        self.b = random.randint(3, 15)
        # Угол C (в градусах) так, чтобы треугольник был валидным
        self.angle_C = random.choice([30, 45, 60, 90, 120])
        
        # Вычисляем сторону c по теореме косинусов
        angle_C_rad = math.radians(self.angle_C)
        self.c = math.sqrt(self.a**2 + self.b**2 - 2*self.a*self.b*math.cos(angle_C_rad))
        
        if self.language == "ru":
            self.given = f"a = {self.a}, b = {self.b}, ∠C = {self.angle_C}°"
            self.find = "сторону c"
        else:
            self.given = f"a = {self.a}, b = {self.b}, ∠C = {self.angle_C}°"
            self.find = "side c"
    
    def _generate_inverse_params(self):
        """Генерирует параметры для обратной функции."""
        self.func = random.choice(["arcsin", "arccos", "arctan"])
        
        if self.func == "arcsin":
            values = [0, 0.5, -0.5, 1, -1]
            self.value = random.choice(values)
            self.value_str = str(Fraction(self.value).limit_denominator()) if self.value != int(self.value) else str(int(self.value))
        elif self.func == "arccos":
            values = [0, 0.5, -0.5, 1, -1]
            self.value = random.choice(values)
            self.value_str = str(Fraction(self.value).limit_denominator()) if self.value != int(self.value) else str(int(self.value))
        else:  # arctan
            values = [0, 1, -1]
            self.value = random.choice(values)
            self.value_str = str(self.value)
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("trigonometry", {}).get("problem", {})
        
        if self.task_type == "basic_value":
            template = templates.get("basic_value", {}).get(self.language, "")
            return template.format(func=self.func, angle=self.angle_rad)
        
        elif self.task_type == "equation":
            template = templates.get("equation", {}).get(self.language, "")
            return template.format(equation=self.equation, interval=self.interval)
        
        elif self.task_type == "identity":
            template = templates.get("identity", {}).get(self.language, "")
            return template.format(expression=self.expression)
        
        elif self.task_type == "triangle_solve":
            template = templates.get("triangle_solve", {}).get(self.language, "")
            return template.format(given=self.given, find=self.find)
        
        elif self.task_type == "inverse":
            template = templates.get("inverse", {}).get(self.language, "")
            return template.format(func=self.func, value=self.value_str)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("trigonometry", {}).get("steps", {})
        
        if self.task_type == "basic_value":
            self._solve_basic_value(steps_templates)
        elif self.task_type == "equation":
            self._solve_equation(steps_templates)
        elif self.task_type == "identity":
            self._solve_identity(steps_templates)
        elif self.task_type == "triangle_solve":
            self._solve_triangle(steps_templates)
        elif self.task_type == "inverse":
            self._solve_inverse(steps_templates)
    
    def _solve_basic_value(self, templates):
        """Вычисление значения тригонометрической функции."""
        exact_val = self.EXACT_VALUES.get(self.angle_deg, {}).get(self.func, "")
        
        template = templates.get("basic_value_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, func=self.func, angle=self.angle_rad, result=exact_val
        ))
        
        self.final_answer = exact_val
    
    def _solve_equation(self, templates):
        """Решение тригонометрического уравнения."""
        # Упрощённое решение для основных случаев
        if self.eq_key == "sin_half":  # 2sin(x) - 1 = 0 => sin(x) = 1/2
            solutions = "π/6, 5π/6"
        elif self.eq_key == "cos_neg_half":  # 2cos(x) + 1 = 0 => cos(x) = -1/2
            solutions = "2π/3, 4π/3"
        elif self.eq_key == "sin_double":  # sin(2x) = 0
            solutions = "0, π/2, π, 3π/2, 2π"
        elif self.eq_key == "tan_one":  # tan(x) = 1
            solutions = "π/4, 5π/4"
        else:
            solutions = "решения зависят от значения" if self.language == "ru" else "solutions depend on the value"
        
        template1 = templates.get("equation_transform", {}).get(self.language, "")
        self.solution_steps.append(template1.format(step=1, transformed=self.equation))
        
        template2 = templates.get("equation_solutions", {}).get(self.language, "")
        self.solution_steps.append(template2.format(step=2, solutions=solutions))
        
        self.final_answer = f"x = {solutions}"
    
    def _solve_identity(self, templates):
        """Упрощение тригонометрического тождества."""
        template = templates.get("identity_apply", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, identity=f"{self.expression} = {self.simplified}"))
        
        self.final_answer = self.simplified
    
    def _solve_triangle(self, templates):
        """Решение треугольника."""
        misc = PROMPT_TEMPLATES.get("trigonometry", {}).get("misc", {})
        
        template = templates.get("law_of_cosines", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1))
        
        step2 = misc.get("triangle_step2", {}).get(self.language, "")
        self.solution_steps.append(step2.format(a=self.a, b=self.b, angle=self.angle_C))
        
        step3 = misc.get("triangle_step3", {}).get(self.language, "")
        self.solution_steps.append(step3.format(result=f"{self.c:.4f}"))
        
        self.final_answer = f"c = {self.c:.4f}"
    
    def _solve_inverse(self, templates):
        """Вычисление обратной функции."""
        if self.func == "arcsin":
            result_map = {0: "0", 0.5: "π/6", -0.5: "-π/6", 1: "π/2", -1: "-π/2"}
        elif self.func == "arccos":
            result_map = {0: "π/2", 0.5: "π/3", -0.5: "2π/3", 1: "0", -1: "π"}
        else:  # arctan
            result_map = {0: "0", 1: "π/4", -1: "-π/4"}
        
        result = result_map.get(self.value, str(math.atan(self.value)))
        
        template = templates.get("basic_value_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, func=self.func, angle=self.value_str, result=result
        ))
        
        self.final_answer = result
    
    def get_task_type(self) -> str:
        return "trigonometry"
    
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
        """Генерирует случайную тригонометрическую задачу."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format,
            reasoning_mode=reasoning_mode
        )
