# re_rl/tasks/logarithmic_task.py

import math
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Dict, Any, Optional

class LogarithmicTask(BaseMathTask):
    """Класс для генерации и решения логарифмических уравнений вида a*log(b*x) + c = d"""
    
    def __init__(self, a, b, c, d, language="ru", detail_level=3):
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
        description = PROMPT_TEMPLATES["logarithmic"]["problem"][language].format(
            left=f"{self.a}*log({self.b}*x) + {self.c}",
            d=self.d
        )
        super().__init__(description, language, detail_level)
        
    def solve(self):
        """
        Решает логарифмическое уравнение с заданным уровнем детализации.
        Заполняет self.solution_steps, self.explanation_steps, self.validation_steps и self.final_answer.
        """
        detail_level = self.detail_level
        
        # Шаг 1: Записываем уравнение
        if detail_level >= 1:
            if self.language == "ru":
                step = f"Записываем уравнение: {self.a} * log({self.b} * x) + {self.c} = {self.d}"
                explanation = "Записываем исходное уравнение"
                validation = "Уравнение записано корректно"
            else:
                step = f"Write the equation: {self.a} * log({self.b} * x) + {self.c} = {self.d}"
                explanation = "Write down the original equation"
                validation = "Equation is written correctly"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 2: Анализируем уравнение
        if detail_level >= 2:
            if self.language == "ru":
                step = f"Анализируем уравнение:\n- Коэффициент при логарифме: {self.a}\n- Коэффициент при x: {self.b}\n- Свободный член: {self.c}\n- Правая часть: {self.d}"
                explanation = "Анализируем структуру уравнения"
                validation = "Анализ выполнен правильно"
            else:
                step = f"Analyze the equation:\n- Coefficient of logarithm: {self.a}\n- Coefficient of x: {self.b}\n- Constant term: {self.c}\n- Right side: {self.d}"
                explanation = "Analyze the equation structure"
                validation = "Analysis is correct"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 3: Переносим свободный член
        right_side = self.d - self.c
        if detail_level >= 3:
            if self.language == "ru":
                step = f"Переносим свободный член {self.c} в правую часть:\n{self.a} * log({self.b} * x) = {self.d} - {self.c} = {right_side}"
                explanation = "Переносим свободный член в правую часть"
                validation = "Перенос выполнен правильно"
            else:
                step = f"Move constant term {self.c} to the right side:\n{self.a} * log({self.b} * x) = {self.d} - {self.c} = {right_side}"
                explanation = "Move constant term to the right side"
                validation = "Transfer is performed correctly"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 4: Делим обе части
        log_value = right_side / self.a
        if detail_level >= 4:
            if self.language == "ru":
                step = f"Делим обе части на {self.a}:\nlog({self.b} * x) = {right_side} / {self.a} = {log_value}"
                explanation = "Делим обе части на коэффициент при логарифме"
                validation = "Деление выполнено правильно"
            else:
                step = f"Divide both sides by {self.a}:\nlog({self.b} * x) = {right_side} / {self.a} = {log_value}"
                explanation = "Divide both sides by coefficient of logarithm"
                validation = "Division is performed correctly"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 5: Применяем экспоненту
        exp_value = math.exp(log_value)
        if detail_level >= 5:
            if self.language == "ru":
                step = f"Применяем экспоненту к обеим частям:\n{self.b} * x = e^{log_value} = {exp_value:.6f}"
                explanation = "Применяем экспоненту для избавления от логарифма"
                validation = "Экспонента применена правильно"
            else:
                step = f"Apply exponential to both sides:\n{self.b} * x = e^{log_value} = {exp_value:.6f}"
                explanation = "Apply exponential to eliminate logarithm"
                validation = "Exponential is applied correctly"
            self.add_solution_step(step, explanation, validation)
        
        # Вычисляем решение
        x = exp_value / self.b
        
        # Шаг 6: Решаем уравнение
        if detail_level >= 6:
            if self.language == "ru":
                step = f"Решаем относительно x:\nx = {exp_value:.6f} / {self.b} = {x}"
                explanation = "Решаем полученное уравнение"
                validation = "Решение выполнено правильно"
            else:
                step = f"Solve for x:\nx = {exp_value:.6f} / {self.b} = {x}"
                explanation = "Solve the resulting equation"
                validation = "Solution is correct"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 7: Проверяем решение
        if detail_level >= 7:
            check_value = self.a * math.log(self.b * x) + self.c
            if self.language == "ru":
                step = f"Проверяем решение:\n{self.a} * log({self.b} * {x}) + {self.c} = {check_value:.6f} ≈ {self.d}"
                explanation = "Проверяем полученное решение"
                validation = "Проверка подтверждает корректность решения"
            else:
                step = f"Verify the solution:\n{self.a} * log({self.b} * {x}) + {self.c} = {check_value:.6f} ≈ {self.d}"
                explanation = "Verify the solution"
                validation = "Verification confirms the solution is correct"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 8: Геометрическая интерпретация
        if detail_level >= 8:
            if self.language == "ru":
                step = "Геометрическая интерпретация: точка пересечения логарифмической функции y = a*log(b*x) + c с горизонтальной прямой y = d"
                explanation = "Даем геометрическую интерпретацию решения"
                validation = "Геометрическая интерпретация верна"
            else:
                step = "Geometric interpretation: intersection point of logarithmic function y = a*log(b*x) + c with horizontal line y = d"
                explanation = "Provide geometric interpretation of the solution"
                validation = "Geometric interpretation is correct"
            self.add_solution_step(step, explanation, validation)
        
        # Шаг 9: Проверка области определения
        if detail_level >= 9:
            if self.language == "ru":
                step = f"Проверяем область определения: {self.b} * x = {self.b * x:.6f} > 0 ✓"
                explanation = "Проверяем область определения логарифмической функции"
                validation = "Решение принадлежит области определения"
            else:
                step = f"Check the domain: {self.b} * x = {self.b * x:.6f} > 0 ✓"
                explanation = "Check the domain of logarithmic function"
                validation = "Solution belongs to the domain"
            self.add_solution_step(step, explanation, validation)
        
        self.final_answer = x

    def get_task_type(self):
        return "logarithmic"
