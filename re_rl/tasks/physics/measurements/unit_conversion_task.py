# re_rl/tasks/physics/measurements/unit_conversion_task.py

import random
from typing import Dict, Any, ClassVar

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class UnitConversionTask(BaseMathTask):
    """Задачи на перевод единиц измерения."""
    
    TASK_TYPES = ["simple", "compound", "derived"]
    
    # Коэффициенты перевода
    CONVERSIONS = {
        # length
        ("км", "м"): 1000,
        ("м", "см"): 100,
        ("м", "мм"): 1000,
        ("миля", "км"): 1.609,
        ("фут", "м"): 0.3048,
        ("дюйм", "см"): 2.54,
        # mass
        ("кг", "г"): 1000,
        ("т", "кг"): 1000,
        ("фунт", "кг"): 0.4536,
        # time
        ("ч", "мин"): 60,
        ("мин", "с"): 60,
        ("сут", "ч"): 24,
        # speed
        ("км/ч", "м/с"): 1/3.6,
        ("м/с", "км/ч"): 3.6,
        # energy
        ("кДж", "Дж"): 1000,
        ("эВ", "Дж"): 1.602e-19,
        ("кал", "Дж"): 4.186,
        # pressure
        ("атм", "Па"): 101325,
        ("бар", "Па"): 100000,
        ("мм рт.ст.", "Па"): 133.322,
        # temperature
        ("°C", "K"): ("add", 273.15),  # особый случай
    }

    def __init__(self, language="ru", detail_level=3, task_type=None, difficulty=None, output_format="text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self.task_type = task_type or random.choice(self.TASK_TYPES)
        
        # Выбираем случайную конверсию
        self.conversion = random.choice(list(self.CONVERSIONS.keys()))
        self.factor = self.CONVERSIONS[self.conversion]
        
        # Генерируем значение
        self.value = round(random.uniform(1, 1000), 2)
        
        problem_text = self._create_problem_text()
        super().__init__(problem_text, language, detail_level, output_format)

    def _create_problem_text(self):
        t = PROMPT_TEMPLATES["unit_conversion"]
        text = t["instructions"][self.language] + "\n\n"
        
        from_unit, to_unit = self.conversion
        
        if self.task_type == "simple":
            text += t["problem"]["simple"][self.language].format(
                value=self.value, from_unit=from_unit, to_unit=to_unit)
        elif self.task_type == "compound":
            text += t["problem"]["compound"][self.language].format(
                value=self.value, from_unit=from_unit)
        else:
            text += t["problem"]["derived"][self.language].format(
                value=self.value, from_unit=from_unit)
        return text

    def solve(self):
        t = PROMPT_TEMPLATES["unit_conversion"]
        steps = []
        
        from_unit, to_unit = self.conversion
        
        if isinstance(self.factor, tuple):
            # Температура
            if self.factor[0] == "add":
                result = self.value + self.factor[1]
                steps.append(f"K = °C + 273.15")
                steps.append(f"{self.value} + 273.15 = {round(result, 2)}")
        else:
            steps.append(t["steps"]["conversion_factor"][self.language].format(
                from_unit=from_unit, factor=self.factor, to_unit=to_unit))
            result = self.value * self.factor
            steps.append(t["steps"]["calculate"][self.language].format(
                value=self.value, factor=self.factor, result=f"{result:.6g}"))
        
        # Ограничиваем количество шагов (без дублирования)
        self.solution_steps = steps[:self.detail_level]
        
        if isinstance(self.factor, tuple):
            answer = f"{self.value} {from_unit} = {round(result, 2)} {to_unit}"
        else:
            answer = f"{self.value} {from_unit} = {result:.6g} {to_unit}"
        self.final_answer = t["final_answer"][self.language].format(answer=answer)

    def get_task_type(self):
        return "unit_conversion"
    
    @classmethod
    def generate_random_task(cls, **kwargs):
        return cls(**kwargs)
