# re_rl/tasks/logarithmic_task.py

import math
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, Optional

class LogarithmicTask(BaseMathTask):
    """Класс для генерации и решения логарифмических уравнений вида a*log(b*x) + c = d"""
    
    def __init__(self, a, b, c, d, language="ru", detail_level=1):
        """
        Инициализация логарифмического уравнения
        
        Args:
            a (float): Коэффициент при логарифме
            b (float): Коэффициент при x в аргументе логарифма
            c (float): Свободный член
            d (float): Правая часть уравнения
            language (str): Язык ("ru" или "en")
            detail_level (int): Уровень детализации решения (1-9)
        """
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.equation = f"{a}*log({b}*x) + {c} = {d}"
        self.solution = None
        description = PROMPT_TEMPLATES["logarithmic"]["problem"][language].format(
            left=f"{self.a}*log({self.b}*x) + {self.c}",
            d=self.d
        )
        super().__init__(description, language, detail_level)
        
    def solve(self, detail_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Решает логарифмическое уравнение с заданным уровнем детализации.
        
        Args:
            detail_level: Уровень детализации решения (1-9). Если не указан, используется self.detail_level
            
        Returns:
            Dict[str, Any]: Результат решения
        """
        if detail_level is None:
            detail_level = self.detail_level
        
        result = {
            "description": self.description,
            "solution_steps": [],
            "final_answer": None,
            "explanations": [],
            "validations": []
        }
        
        # Шаг 1: Записываем уравнение
        if detail_level >= 1:
            result["solution_steps"].append("Записываем уравнение: " + f"{self.a} * log({self.b} * x) + {self.c} = {self.d}")
            result["explanations"].append("Записываем исходное уравнение")
            result["validations"].append("Проверяем корректность записи уравнения")
        
        # Шаг 2: Анализируем уравнение
        if detail_level >= 2:
            result["solution_steps"].append("Анализируем уравнение: " + f"{self.a} * log({self.b} * x) + {self.c} = {self.d}")
            result["explanations"].append("Анализируем структуру уравнения")
            result["validations"].append("Проверяем правильность анализа")
        
        # Шаг 3: Переносим свободный член
        if detail_level >= 3:
            result["solution_steps"].append("Переносим свободный член " + f"{self.c} в правую часть: {self.a} * log({self.b} * x) = {self.d - self.c}")
            result["explanations"].append("Переносим свободный член в правую часть")
            result["validations"].append("Проверяем правильность переноса членов")
        
        # Шаг 4: Делим обе части
        if detail_level >= 4:
            result["solution_steps"].append("Делим обе части на " + f"{self.a}: log({self.b} * x) = {(self.d - self.c) / self.a}")
            result["explanations"].append("Делим обе части на коэффициент при логарифме")
            result["validations"].append("Проверяем правильность деления")
        
        # Шаг 5: Применяем экспоненту
        if detail_level >= 5:
            result["solution_steps"].append("Применяем экспоненту к обеим частям: " + f"{self.b} * x = e^({(self.d - self.c) / self.a})")
            result["explanations"].append("Применяем экспоненту для избавления от логарифма")
            result["validations"].append("Проверяем правильность применения экспоненты")
        
        # Шаг 6: Решаем уравнение
        if detail_level >= 6:
            result["solution_steps"].append("Упрощаем левую часть: " + f"x = e^({(self.d - self.c) / self.a}) / {self.b}")
            result["explanations"].append("Решаем полученное уравнение")
            result["validations"].append("Проверяем правильность решения")
        
        # Шаг 7: Проверяем решение
        if detail_level >= 7:
            x = math.exp((self.d - self.c) / self.a) / self.b
            result["solution_steps"].append("Проверяем решение: " + f"{self.a} * log({self.b} * {x}) + {self.c} = {self.d}")
            result["explanations"].append("Проверяем полученное решение")
            result["validations"].append("Проверяем подстановку решения в исходное уравнение")
        
        # Шаг 8: Геометрическая интерпретация
        if detail_level >= 8:
            result["solution_steps"].append("Геометрическая интерпретация: точка пересечения логарифмической функции с прямой")
            result["explanations"].append("Даем геометрическую интерпретацию решения")
            result["validations"].append("Проверяем корректность геометрической интерпретации")
        
        # Шаг 9: Проверка области определения
        if detail_level >= 9:
            result["solution_steps"].append("Проверяем область определения: " + f"{self.b} * x > 0")
            result["explanations"].append("Проверяем область определения логарифмической функции")
            result["validations"].append("Проверяем принадлежность решения области определения")
        
        # Вычисляем решение
        x = math.exp((self.d - self.c) / self.a) / self.b
        self.final_answer = x
        result["final_answer"] = x
        
        return result

    def get_task_type(self):
        return "logarithmic"
