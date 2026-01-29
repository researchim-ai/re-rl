# re_rl/tasks/statistics_task.py

"""
StatisticsTask — задачи по описательной статистике.

Поддерживаемые типы:
- mean: среднее арифметическое
- median: медиана
- mode: мода
- variance: дисперсия
- std_deviation: стандартное отклонение
- correlation: корреляция Пирсона
- linear_regression: линейная регрессия
- percentile: перцентиль
- quartiles: квартили
- z_score: z-оценка
"""

import random
import math
from collections import Counter
from typing import List, Dict, Any, ClassVar, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class StatisticsTask(BaseMathTask):
    """Генератор задач по статистике."""
    
    TASK_TYPES = [
        "mean", "median", "mode", "variance", "std_deviation",
        "correlation", "linear_regression", "percentile", "quartiles", "z_score"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"data_size": 5, "max_value": 10, "decimals": False},
        2: {"data_size": 6, "max_value": 20, "decimals": False},
        3: {"data_size": 7, "max_value": 30, "decimals": False},
        4: {"data_size": 8, "max_value": 50, "decimals": False},
        5: {"data_size": 10, "max_value": 50, "decimals": True},
        6: {"data_size": 10, "max_value": 100, "decimals": True},
        7: {"data_size": 12, "max_value": 100, "decimals": True},
        8: {"data_size": 15, "max_value": 100, "decimals": True},
        9: {"data_size": 15, "max_value": 200, "decimals": True},
        10: {"data_size": 20, "max_value": 500, "decimals": True},
    }
    
    def __init__(
        self,
        task_type: str = "mean",
        data: List[float] = None,
        x_data: List[float] = None,
        y_data: List[float] = None,
        percentile: int = None,
        x_value: float = None,
        mean_value: float = None,
        std_value: float = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.data_size = preset.get("data_size", 10)
        self.max_value = preset.get("max_value", 100)
        self.use_decimals = preset.get("decimals", False)
        
        # Генерируем или используем данные
        self.data = data if data is not None else self._generate_data()
        self.x_data = x_data
        self.y_data = y_data
        self.percentile = percentile or random.choice([25, 50, 75, 90])
        self.x_value = x_value
        self.mean_given = mean_value
        self.std_given = std_value
        
        # Генерируем данные для корреляции/регрессии
        if self.task_type in ["correlation", "linear_regression"] and (x_data is None or y_data is None):
            self._generate_correlation_data()
        
        # Генерируем данные для z-score
        if self.task_type == "z_score":
            if self.x_value is None:
                self.x_value = random.choice(self.data) if self.data else random.randint(1, 100)
            if self.mean_given is None:
                self.mean_given = sum(self.data) / len(self.data) if self.data else 50
            if self.std_given is None:
                mean = self.mean_given
                self.std_given = math.sqrt(sum((x - mean)**2 for x in self.data) / len(self.data)) if self.data else 10
        
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_data(self) -> List[float]:
        """Генерирует набор данных."""
        if self.use_decimals:
            return [round(random.uniform(1, self.max_value), 1) for _ in range(self.data_size)]
        else:
            return [random.randint(1, self.max_value) for _ in range(self.data_size)]
    
    def _generate_correlation_data(self):
        """Генерирует коррелированные данные."""
        n = min(self.data_size, 8)
        self.x_data = [random.randint(1, 20) for _ in range(n)]
        
        # Генерируем y с некоторой корреляцией с x
        slope = random.uniform(0.5, 3)
        intercept = random.uniform(-5, 10)
        noise = random.uniform(1, 5)
        
        self.y_data = [
            round(slope * x + intercept + random.uniform(-noise, noise), 1)
            for x in self.x_data
        ]
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("statistics", {}).get("problem", {})
        
        if self.task_type == "mean":
            template = templates.get("mean", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "median":
            template = templates.get("median", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "mode":
            # Для моды генерируем данные с повторами
            if len(set(self.data)) == len(self.data):
                # Добавляем повторы
                self.data = self.data[:-2] + [self.data[0], self.data[0]]
            template = templates.get("mode", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "variance":
            template = templates.get("variance", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "std_deviation":
            template = templates.get("std_deviation", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "correlation":
            template = templates.get("correlation", {}).get(self.language, "")
            return template.format(x_data=self.x_data, y_data=self.y_data)
        
        elif self.task_type == "linear_regression":
            template = templates.get("linear_regression", {}).get(self.language, "")
            return template.format(x_data=self.x_data, y_data=self.y_data)
        
        elif self.task_type == "percentile":
            template = templates.get("percentile", {}).get(self.language, "")
            return template.format(p=self.percentile, data=self.data)
        
        elif self.task_type == "quartiles":
            template = templates.get("quartiles", {}).get(self.language, "")
            return template.format(data=self.data)
        
        elif self.task_type == "z_score":
            template = templates.get("z_score", {}).get(self.language, "")
            return template.format(x=self.x_value, mean=round(self.mean_given, 2), std=round(self.std_given, 2))
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("statistics", {}).get("steps", {})
        
        if self.task_type == "mean":
            self._solve_mean(templates)
        elif self.task_type == "median":
            self._solve_median(templates)
        elif self.task_type == "mode":
            self._solve_mode(templates)
        elif self.task_type == "variance":
            self._solve_variance(templates)
        elif self.task_type == "std_deviation":
            self._solve_std_deviation(templates)
        elif self.task_type == "correlation":
            self._solve_correlation(templates)
        elif self.task_type == "linear_regression":
            self._solve_linear_regression(templates)
        elif self.task_type == "percentile":
            self._solve_percentile(templates)
        elif self.task_type == "quartiles":
            self._solve_quartiles(templates)
        elif self.task_type == "z_score":
            self._solve_z_score(templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_mean(self, templates):
        """Среднее арифметическое."""
        total = sum(self.data)
        n = len(self.data)
        mean = total / n
        
        values_str = " + ".join(str(x) for x in self.data)
        
        step1 = templates.get("sum_values", {}).get(self.language, "")
        self.solution_steps.append(step1.format(values=values_str, sum=total))
        
        step2 = templates.get("count_values", {}).get(self.language, "")
        self.solution_steps.append(step2.format(n=n))
        
        step3 = templates.get("mean_formula", {}).get(self.language, "")
        self.solution_steps.append(step3.format(sum=total, n=n, mean=round(mean, 4)))
        
        self.final_answer = f"{mean:.4f}"
    
    def _solve_median(self, templates):
        """Медиана."""
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        
        step1 = templates.get("sort_data", {}).get(self.language, "")
        self.solution_steps.append(step1.format(sorted_data=sorted_data))
        
        if n % 2 == 1:
            median = sorted_data[n // 2]
            step2 = templates.get("median_odd", {}).get(self.language, "")
            self.solution_steps.append(step2.format(n=n, pos=n // 2, median=median))
        else:
            a = sorted_data[n // 2 - 1]
            b = sorted_data[n // 2]
            median = (a + b) / 2
            step2 = templates.get("median_even", {}).get(self.language, "")
            self.solution_steps.append(step2.format(n=n, a=a, b=b, median=median))
        
        self.final_answer = f"{median}"
    
    def _solve_mode(self, templates):
        """Мода."""
        freq = Counter(self.data)
        
        step1 = templates.get("mode_count", {}).get(self.language, "")
        freq_str = ", ".join(f"{k}: {v}" for k, v in sorted(freq.items()))
        self.solution_steps.append(step1.format(freq=freq_str))
        
        max_freq = max(freq.values())
        modes = [k for k, v in freq.items() if v == max_freq]
        
        step2 = templates.get("mode_result", {}).get(self.language, "")
        mode_str = ", ".join(str(m) for m in modes) if len(modes) > 1 else str(modes[0])
        self.solution_steps.append(step2.format(mode=mode_str))
        
        self.final_answer = mode_str
    
    def _solve_variance(self, templates):
        """Дисперсия."""
        n = len(self.data)
        mean = sum(self.data) / n
        deviations = [x - mean for x in self.data]
        squared = [d ** 2 for d in deviations]
        variance = sum(squared) / n
        
        dev_str = ", ".join(f"{round(d, 2)}" for d in deviations)
        step1 = templates.get("variance_deviations", {}).get(self.language, "")
        self.solution_steps.append(step1.format(deviations=dev_str))
        
        sq_str = ", ".join(f"{round(s, 2)}" for s in squared)
        step2 = templates.get("variance_squared", {}).get(self.language, "")
        self.solution_steps.append(step2.format(squared=sq_str))
        
        step3 = templates.get("variance_formula", {}).get(self.language, "")
        self.solution_steps.append(step3.format(sum_sq=round(sum(squared), 4), n=n, variance=round(variance, 4)))
        
        self.final_answer = f"{variance:.4f}"
    
    def _solve_std_deviation(self, templates):
        """Стандартное отклонение."""
        n = len(self.data)
        mean = sum(self.data) / n
        variance = sum((x - mean) ** 2 for x in self.data) / n
        std = math.sqrt(variance)
        
        # Сначала показываем шаги дисперсии
        step3 = templates.get("variance_formula", {}).get(self.language, "")
        self.solution_steps.append(step3.format(sum_sq=round(variance * n, 4), n=n, variance=round(variance, 4)))
        
        step4 = templates.get("std_formula", {}).get(self.language, "")
        self.solution_steps.append(step4.format(variance=round(variance, 4), std=round(std, 4)))
        
        self.final_answer = f"{std:.4f}"
    
    def _solve_correlation(self, templates):
        """Корреляция Пирсона."""
        n = len(self.x_data)
        mean_x = sum(self.x_data) / n
        mean_y = sum(self.y_data) / n
        
        numerator = sum((self.x_data[i] - mean_x) * (self.y_data[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x - mean_x) ** 2 for x in self.x_data)
        sum_sq_y = sum((y - mean_y) ** 2 for y in self.y_data)
        
        denominator = math.sqrt(sum_sq_x * sum_sq_y)
        r = numerator / denominator if denominator != 0 else 0
        
        step = templates.get("correlation_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(step=1, r=round(r, 4)))
        
        self.final_answer = f"r = {r:.4f}"
    
    def _solve_linear_regression(self, templates):
        """Линейная регрессия."""
        n = len(self.x_data)
        mean_x = sum(self.x_data) / n
        mean_y = sum(self.y_data) / n
        
        numerator = sum((self.x_data[i] - mean_x) * (self.y_data[i] - mean_y) for i in range(n))
        denominator = sum((x - mean_x) ** 2 for x in self.x_data)
        
        b = numerator / denominator if denominator != 0 else 0
        a = mean_y - b * mean_x
        
        step1 = templates.get("regression_slope", {}).get(self.language, "")
        self.solution_steps.append(step1.format(step=1, b=round(b, 4)))
        
        step2 = templates.get("regression_intercept", {}).get(self.language, "")
        self.solution_steps.append(step2.format(step=2, a=round(a, 4)))
        
        self.final_answer = f"y = {a:.4f} + {b:.4f}x"
    
    def _solve_percentile(self, templates):
        """Перцентиль."""
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        
        step1 = templates.get("sort_data", {}).get(self.language, "")
        self.solution_steps.append(step1.format(sorted_data=sorted_data))
        
        # Линейная интерполяция
        rank = (self.percentile / 100) * (n - 1)
        lower = int(rank)
        upper = lower + 1
        weight = rank - lower
        
        if upper >= n:
            percentile_value = sorted_data[-1]
        else:
            percentile_value = sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
        
        self.final_answer = f"{percentile_value:.4f}"
    
    def _solve_quartiles(self, templates):
        """Квартили."""
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        
        step1 = templates.get("sort_data", {}).get(self.language, "")
        self.solution_steps.append(step1.format(sorted_data=sorted_data))
        
        def percentile(p):
            rank = (p / 100) * (n - 1)
            lower = int(rank)
            upper = min(lower + 1, n - 1)
            weight = rank - lower
            return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
        
        q1 = percentile(25)
        q2 = percentile(50)
        q3 = percentile(75)
        
        self.final_answer = f"Q1 = {q1:.2f}, Q2 = {q2:.2f}, Q3 = {q3:.2f}"
    
    def _solve_z_score(self, templates):
        """Z-оценка."""
        z = (self.x_value - self.mean_given) / self.std_given if self.std_given != 0 else 0
        
        step = templates.get("z_score_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(
            x=self.x_value, mean=round(self.mean_given, 2), 
            std=round(self.std_given, 2), z=round(z, 4)
        ))
        
        self.final_answer = f"z = {z:.4f}"
    
    def get_task_type(self) -> str:
        return "statistics"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу по статистике."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
