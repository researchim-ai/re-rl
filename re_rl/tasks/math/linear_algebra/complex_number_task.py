# re_rl/tasks/complex_number_task.py

"""
ComplexNumberTask — задачи с комплексными числами.

Поддерживаемые типы:
- arithmetic: арифметические операции
- modulus: модуль комплексного числа
- argument: аргумент комплексного числа
- polar_form: тригонометрическая форма
- power: возведение в степень (формула Муавра)
- roots: корни из комплексного числа
- conjugate: сопряжённое число
- equation: уравнения с комплексными числами
"""

import random
import math
import cmath
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ComplexNumberTask(BaseMathTask):
    """Задачи с комплексными числами."""
    
    TASK_TYPES = [
        "arithmetic", "modulus", "argument", "polar_form",
        "power", "roots", "conjugate", "equation"
    ]
    
    OPERATIONS = ["+", "-", "*", "/"]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_value": 5, "max_power": 2},
        2: {"max_value": 10, "max_power": 3},
        3: {"max_value": 15, "max_power": 4},
        4: {"max_value": 20, "max_power": 5},
        5: {"max_value": 25, "max_power": 6},
        6: {"max_value": 30, "max_power": 7},
        7: {"max_value": 40, "max_power": 8},
        8: {"max_value": 50, "max_power": 10},
        9: {"max_value": 75, "max_power": 12},
        10: {"max_value": 100, "max_power": 15},
    }
    
    def __init__(
        self,
        task_type: str = "arithmetic",
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
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_value = kwargs.get("max_value", preset.get("max_value", 25))
        self.max_power = kwargs.get("max_power", preset.get("max_power", 6))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _rand_part(self) -> int:
        """Генерирует случайную часть комплексного числа."""
        return random.randint(-self.max_value, self.max_value)
    
    def _format_complex(self, a: int, b: int) -> str:
        """Форматирует комплексное число."""
        if b == 0:
            return str(a)
        elif a == 0:
            if b == 1:
                return "i"
            elif b == -1:
                return "-i"
            else:
                return f"{b}i"
        else:
            if b == 1:
                return f"{a} + i"
            elif b == -1:
                return f"{a} - i"
            elif b > 0:
                return f"{a} + {b}i"
            else:
                return f"{a} - {abs(b)}i"
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type == "arithmetic":
            self.a1 = self._rand_part()
            self.b1 = self._rand_part()
            self.a2 = self._rand_part()
            self.b2 = self._rand_part()
            self.op = random.choice(self.OPERATIONS)
            # Избегаем деления на 0
            if self.op == "/" and self.a2 == 0 and self.b2 == 0:
                self.a2 = random.randint(1, self.max_value)
        
        elif self.task_type in ["modulus", "argument", "polar_form", "conjugate"]:
            self.a = self._rand_part()
            self.b = self._rand_part()
            # Не нулевое число
            while self.a == 0 and self.b == 0:
                self.a = self._rand_part()
                self.b = self._rand_part()
        
        elif self.task_type == "power":
            self.a = self._rand_part()
            self.b = self._rand_part()
            while self.a == 0 and self.b == 0:
                self.a = self._rand_part()
                self.b = self._rand_part()
            self.n = random.randint(2, self.max_power)
        
        elif self.task_type == "roots":
            self.a = self._rand_part()
            self.b = self._rand_part()
            while self.a == 0 and self.b == 0:
                self.a = self._rand_part()
                self.b = self._rand_part()
            self.n = random.randint(2, min(5, self.max_power))
        
        elif self.task_type == "equation":
            # z² + az + b = 0
            self.coef_a = self._rand_part()
            self.coef_b = self._rand_part()
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("complex_number", {}).get("problem", {})
        
        if self.task_type == "arithmetic":
            template = templates.get("arithmetic", {}).get(self.language, "")
            return template.format(
                a1=self.a1, b1=self.b1, op=self.op, a2=self.a2, b2=self.b2
            )
        
        elif self.task_type == "modulus":
            template = templates.get("modulus", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b)
        
        elif self.task_type == "argument":
            template = templates.get("argument", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b)
        
        elif self.task_type == "polar_form":
            template = templates.get("polar_form", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b)
        
        elif self.task_type == "power":
            template = templates.get("power", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, n=self.n)
        
        elif self.task_type == "roots":
            template = templates.get("roots", {}).get(self.language, "")
            return template.format(n=self.n, a=self.a, b=self.b)
        
        elif self.task_type == "conjugate":
            template = templates.get("conjugate", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b)
        
        elif self.task_type == "equation":
            template = templates.get("equation", {}).get(self.language, "")
            return template.format(equation=f"z² + {self.coef_a}z + {self.coef_b} = 0")
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("complex_number", {}).get("steps", {})
        
        if self.task_type == "arithmetic":
            self._solve_arithmetic(steps_templates)
        elif self.task_type == "modulus":
            self._solve_modulus(steps_templates)
        elif self.task_type == "argument":
            self._solve_argument(steps_templates)
        elif self.task_type == "polar_form":
            self._solve_polar_form(steps_templates)
        elif self.task_type == "power":
            self._solve_power(steps_templates)
        elif self.task_type == "roots":
            self._solve_roots(steps_templates)
        elif self.task_type == "conjugate":
            self._solve_conjugate(steps_templates)
        elif self.task_type == "equation":
            self._solve_equation(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_arithmetic(self, templates):
        """Арифметические операции с комплексными числами."""
        z1 = complex(self.a1, self.b1)
        z2 = complex(self.a2, self.b2)
        
        if self.op == "+":
            result = z1 + z2
            template = templates.get("add", {}).get(self.language, "")
        elif self.op == "-":
            result = z1 - z2
            template = templates.get("subtract", {}).get(self.language, "")
        elif self.op == "*":
            result = z1 * z2
            template = templates.get("multiply", {}).get(self.language, "")
        else:  # /
            result = z1 / z2
            template = templates.get("divide", {}).get(self.language, "")
        
        result_str = self._format_complex(round(result.real, 4), round(result.imag, 4))
        self.solution_steps.append(template.format(
            step=1, a1=self.a1, b1=self.b1, a2=self.a2, b2=self.b2, result=result_str
        ))
        
        self.final_answer = result_str
    
    def _solve_modulus(self, templates):
        """Модуль комплексного числа."""
        modulus = math.sqrt(self.a ** 2 + self.b ** 2)
        
        template = templates.get("modulus_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, a=self.a, b=self.b, result=f"{modulus:.4f}"
        ))
        
        self.final_answer = f"{modulus:.4f}"
    
    def _solve_argument(self, templates):
        """Аргумент комплексного числа."""
        z = complex(self.a, self.b)
        argument = cmath.phase(z)
        argument_deg = math.degrees(argument)
        
        template = templates.get("argument_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, a=self.a, b=self.b, result=f"{argument:.4f} рад ({argument_deg:.2f}°)"
        ))
        
        self.final_answer = f"{argument:.4f} рад ({argument_deg:.2f}°)"
    
    def _solve_polar_form(self, templates):
        """Тригонометрическая форма."""
        z = complex(self.a, self.b)
        r = abs(z)
        phi = cmath.phase(z)
        
        template = templates.get("polar_form_result", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, r=f"{r:.4f}", phi=f"{phi:.4f}"
        ))
        
        self.final_answer = f"{r:.4f}(cos({phi:.4f}) + i·sin({phi:.4f}))"
    
    def _solve_power(self, templates):
        """Возведение в степень (формула Муавра)."""
        z = complex(self.a, self.b)
        result = z ** self.n
        
        template = templates.get("de_moivre", {}).get(self.language, "")
        result_str = self._format_complex(round(result.real, 4), round(result.imag, 4))
        self.solution_steps.append(template.format(step=1, result=result_str))
        
        self.final_answer = result_str
    
    def _solve_roots(self, templates):
        """Корни n-й степени."""
        z = complex(self.a, self.b)
        r = abs(z)
        phi = cmath.phase(z)
        
        # n-й корень из r
        r_root = r ** (1 / self.n)
        
        template = templates.get("root_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n))
        
        roots = []
        for k in range(self.n):
            angle = (phi + 2 * math.pi * k) / self.n
            root = r_root * cmath.exp(1j * angle)
            root_str = self._format_complex(round(root.real, 4), round(root.imag, 4))
            roots.append(root_str)
            
            template_k = templates.get("root_k", {}).get(self.language, "")
            if k < 3:  # Показываем первые 3 корня
                self.solution_steps.append(template_k.format(step=k+2, k=k, result=root_str))
        
        self.final_answer = ", ".join(roots)
    
    def _solve_conjugate(self, templates):
        """Сопряжённое число."""
        result_str = self._format_complex(self.a, -self.b)
        
        misc = PROMPT_TEMPLATES.get("complex_number", {}).get("misc", {})
        step = misc.get("conjugate_step", {}).get(self.language, "")
        self.solution_steps.append(step.format(
            z=self._format_complex(self.a, self.b), 
            conjugate=result_str
        ))
        
        self.final_answer = result_str
    
    def _solve_equation(self, templates):
        """Решение квадратного уравнения."""
        # z² + az + b = 0
        discriminant = self.coef_a ** 2 - 4 * self.coef_b
        
        if discriminant >= 0:
            z1 = (-self.coef_a + math.sqrt(discriminant)) / 2
            z2 = (-self.coef_a - math.sqrt(discriminant)) / 2
            result = f"z₁ = {z1:.4f}, z₂ = {z2:.4f}"
        else:
            real_part = -self.coef_a / 2
            imag_part = math.sqrt(-discriminant) / 2
            z1_str = self._format_complex(round(real_part, 4), round(imag_part, 4))
            z2_str = self._format_complex(round(real_part, 4), round(-imag_part, 4))
            result = f"z₁ = {z1_str}, z₂ = {z2_str}"
        
        misc = PROMPT_TEMPLATES.get("complex_number", {}).get("misc", {})
        
        step1 = misc.get("discriminant_step", {}).get(self.language, "")
        self.solution_steps.append(step1.format(a=self.coef_a, b=self.coef_b, discriminant=discriminant))
        
        step2 = misc.get("roots_step", {}).get(self.language, "")
        self.solution_steps.append(step2.format(roots=result))
        
        self.final_answer = result
    
    def get_task_type(self) -> str:
        return "complex_number"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу с комплексными числами."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
