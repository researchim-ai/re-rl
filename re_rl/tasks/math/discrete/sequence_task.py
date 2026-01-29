# re_rl/tasks/sequence_task.py

"""
SequenceTask — задачи на последовательности.

Поддерживаемые типы:
- arithmetic_nth: n-й член арифметической прогрессии
- arithmetic_sum: сумма арифметической прогрессии
- geometric_nth: n-й член геометрической прогрессии
- geometric_sum: сумма геометрической прогрессии
- fibonacci_nth: n-е число Фибоначчи
- recurrence: рекуррентные соотношения
- pattern: найти закономерность
- series_sum: сумма ряда
"""

import random
import math
from typing import List, Dict, Any, Optional, Callable, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class SequenceTask(BaseMathTask):
    """Задачи на последовательности."""
    
    TASK_TYPES = [
        "arithmetic_nth", "arithmetic_sum", "geometric_nth", "geometric_sum",
        "fibonacci_nth", "recurrence", "pattern", "series_sum"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_n": 10, "max_value": 20},
        2: {"max_n": 15, "max_value": 50},
        3: {"max_n": 20, "max_value": 100},
        4: {"max_n": 30, "max_value": 200},
        5: {"max_n": 50, "max_value": 500},
        6: {"max_n": 75, "max_value": 1000},
        7: {"max_n": 100, "max_value": 2000},
        8: {"max_n": 150, "max_value": 5000},
        9: {"max_n": 200, "max_value": 10000},
        10: {"max_n": 500, "max_value": 50000},
    }
    
    # Паттерны последовательностей для типа "pattern"
    PATTERNS = [
        ("squares", lambda n: n ** 2, "n²"),
        ("cubes", lambda n: n ** 3, "n³"),
        ("triangular", lambda n: n * (n + 1) // 2, "n(n+1)/2"),
        ("powers_of_2", lambda n: 2 ** n, "2^n"),
        ("factorial", lambda n: math.factorial(n), "n!"),
        ("primes", None, "простые числа"),  # Обрабатывается отдельно
        ("double_plus_one", lambda n: 2 * n + 1, "2n + 1"),
        ("alternating", lambda n: (-1) ** n * n, "(-1)^n × n"),
    ]
    
    def __init__(
        self,
        task_type: str = "arithmetic_nth",
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self.kwargs = kwargs
        
        # Получаем параметры из пресета
        preset = self._interpolate_difficulty(difficulty)
        self.max_n = kwargs.get("max_n", preset.get("max_n", 50))
        self.max_value = kwargs.get("max_value", preset.get("max_value", 500))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type in ["arithmetic_nth", "arithmetic_sum"]:
            self.a1 = self.kwargs.get("a1", random.randint(-20, 20))
            self.d = self.kwargs.get("d", random.randint(-10, 10))
            while self.d == 0:
                self.d = random.randint(-10, 10)
            self.n = self.kwargs.get("n", random.randint(5, min(50, self.max_n)))
        
        elif self.task_type in ["geometric_nth", "geometric_sum"]:
            self.a1 = self.kwargs.get("a1", random.randint(1, 10))
            self.r = self.kwargs.get("r", random.choice([-3, -2, 2, 3, 4, 5]))
            self.n = self.kwargs.get("n", random.randint(3, min(10, self.max_n // 5)))
        
        elif self.task_type == "fibonacci_nth":
            self.n = self.kwargs.get("n", random.randint(5, min(30, self.max_n)))
        
        elif self.task_type == "recurrence":
            self._generate_recurrence_params()
        
        elif self.task_type == "pattern":
            self._generate_pattern_params()
        
        elif self.task_type == "series_sum":
            self._generate_series_params()
    
    def _generate_recurrence_params(self):
        """Генерирует параметры для рекуррентного соотношения."""
        # Простые рекуррентные соотношения
        recurrence_types = [
            ("2*a_{n-1}", lambda seq, n: 2 * seq[n-1] if n > 0 else seq[0]),
            ("a_{n-1} + n", lambda seq, n: seq[n-1] + n if n > 0 else seq[0]),
            ("a_{n-1} + a_{n-2}", lambda seq, n: seq[n-1] + seq[n-2] if n > 1 else (seq[n-1] if n > 0 else seq[0])),
            ("3*a_{n-1} - 2", lambda seq, n: 3 * seq[n-1] - 2 if n > 0 else seq[0]),
        ]
        
        self.recurrence_formula, self.recurrence_func = random.choice(recurrence_types)
        self.a1 = self.kwargs.get("a1", random.randint(1, 5))
        self.target = self.kwargs.get("target", random.randint(5, min(15, self.max_n)))
    
    def _generate_pattern_params(self):
        """Генерирует параметры для задачи на закономерность."""
        # Выбираем паттерн
        pattern_name, pattern_func, pattern_desc = random.choice(self.PATTERNS)
        self.pattern_name = pattern_name
        self.pattern_desc = pattern_desc
        
        if pattern_name == "primes":
            # Генерируем простые числа
            self.sequence = self._get_primes(10)[:6]
            self.next_term = self._get_primes(10)[6]
        else:
            self.pattern_func = pattern_func
            self.sequence = [pattern_func(i) for i in range(1, 7)]
            self.next_term = pattern_func(7)
    
    def _get_primes(self, count: int) -> List[int]:
        """Возвращает первые count простых чисел."""
        primes = []
        n = 2
        while len(primes) < count:
            is_prime = True
            for p in primes:
                if p * p > n:
                    break
                if n % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(n)
            n += 1
        return primes
    
    def _generate_series_params(self):
        """Генерирует параметры для суммы ряда."""
        # Простые ряды
        series_types = [
            ("1 + 2 + 3 + ... + n", "arithmetic", None),
            ("1² + 2² + 3² + ... + n²", "squares", lambda n: n * (n + 1) * (2 * n + 1) // 6),
            ("1 + 1/2 + 1/4 + ... (геом.)", "geometric_infinite", lambda: 2),
        ]
        
        self.series_type = random.choice(["arithmetic", "squares"])
        self.n = self.kwargs.get("n", random.randint(5, min(20, self.max_n)))
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("sequence", {}).get("problem", {})
        
        if self.task_type == "arithmetic_nth":
            template = templates.get("arithmetic_nth", {}).get(self.language, "")
            return template.format(n=self.n, a1=self.a1, d=self.d)
        
        elif self.task_type == "arithmetic_sum":
            template = templates.get("arithmetic_sum", {}).get(self.language, "")
            return template.format(n=self.n, a1=self.a1, d=self.d)
        
        elif self.task_type == "geometric_nth":
            template = templates.get("geometric_nth", {}).get(self.language, "")
            return template.format(n=self.n, a1=self.a1, r=self.r)
        
        elif self.task_type == "geometric_sum":
            template = templates.get("geometric_sum", {}).get(self.language, "")
            return template.format(n=self.n, a1=self.a1, r=self.r)
        
        elif self.task_type == "fibonacci_nth":
            template = templates.get("fibonacci_nth", {}).get(self.language, "")
            return template.format(n=self.n)
        
        elif self.task_type == "recurrence":
            template = templates.get("recurrence", {}).get(self.language, "")
            return template.format(formula=self.recurrence_formula, a1=self.a1, target=self.target)
        
        elif self.task_type == "pattern":
            template = templates.get("pattern", {}).get(self.language, "")
            seq_str = ", ".join(map(str, self.sequence))
            return template.format(sequence=seq_str)
        
        elif self.task_type == "series_sum":
            template = templates.get("series_sum", {}).get(self.language, "")
            if self.series_type == "arithmetic":
                series = f"1 + 2 + 3 + ... + {self.n}"
            else:
                series = f"1² + 2² + 3² + ... + {self.n}²"
            return template.format(series=series)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("sequence", {}).get("steps", {})
        
        if self.task_type == "arithmetic_nth":
            self._solve_arithmetic_nth(steps_templates)
        elif self.task_type == "arithmetic_sum":
            self._solve_arithmetic_sum(steps_templates)
        elif self.task_type == "geometric_nth":
            self._solve_geometric_nth(steps_templates)
        elif self.task_type == "geometric_sum":
            self._solve_geometric_sum(steps_templates)
        elif self.task_type == "fibonacci_nth":
            self._solve_fibonacci(steps_templates)
        elif self.task_type == "recurrence":
            self._solve_recurrence(steps_templates)
        elif self.task_type == "pattern":
            self._solve_pattern(steps_templates)
        elif self.task_type == "series_sum":
            self._solve_series_sum(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_arithmetic_nth(self, templates):
        """a_n = a1 + (n-1)*d"""
        result = self.a1 + (self.n - 1) * self.d
        
        template = templates.get("arithmetic_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, a1=self.a1, n=self.n, d=self.d, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_arithmetic_sum(self, templates):
        """S_n = n*(a1 + an)/2"""
        an = self.a1 + (self.n - 1) * self.d
        result = self.n * (self.a1 + an) // 2
        
        # Шаг 1: находим a_n
        template1 = templates.get("arithmetic_formula", {}).get(self.language, "")
        self.solution_steps.append(template1.format(
            step=1, a1=self.a1, n=self.n, d=self.d, result=an
        ))
        
        # Шаг 2: находим сумму
        template2 = templates.get("arithmetic_sum_formula", {}).get(self.language, "")
        self.solution_steps.append(template2.format(
            step=2, n=self.n, a1=self.a1, an=an, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_geometric_nth(self, templates):
        """a_n = a1 * r^(n-1)"""
        result = self.a1 * (self.r ** (self.n - 1))
        
        template = templates.get("geometric_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, a1=self.a1, r=self.r, n=self.n, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_geometric_sum(self, templates):
        """S_n = a1*(r^n - 1)/(r - 1)"""
        if self.r == 1:
            result = self.a1 * self.n
        else:
            result = self.a1 * (self.r ** self.n - 1) // (self.r - 1)
        
        template = templates.get("geometric_sum_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, result=result))
        
        self.final_answer = str(result)
    
    def _solve_fibonacci(self, templates):
        """Числа Фибоначчи."""
        fib = [0, 1]
        for i in range(2, self.n + 1):
            fib.append(fib[-1] + fib[-2])
        
        result = fib[self.n]
        
        # Показываем несколько шагов
        for i in range(min(self.n, 5)):
            if i >= 2:
                template = templates.get("fibonacci_step", {}).get(self.language, "")
                self.solution_steps.append(template.format(
                    step=i-1, n=i, n_minus_1=i-1, n_minus_2=i-2,
                    f1=fib[i-1], f2=fib[i-2], result=fib[i]
                ))
        
        self.final_answer = str(result)
    
    def _solve_recurrence(self, templates):
        """Решение рекуррентного соотношения."""
        seq = [self.a1]
        
        for i in range(1, self.target):
            next_val = self.recurrence_func(seq, i)
            seq.append(next_val)
            
            if i <= 5:
                template = templates.get("recurrence_step", {}).get(self.language, "")
                self.solution_steps.append(template.format(
                    step=i, n=i+1, formula_applied=f"a_{i} = {next_val}", result=next_val
                ))
        
        self.final_answer = str(seq[-1])
    
    def _solve_pattern(self, templates):
        """Определение закономерности."""
        template = templates.get("pattern_identified", {}).get(self.language, "")
        
        if self.language == "ru":
            desc = f"Каждый элемент вычисляется по формуле: {self.pattern_desc}"
        else:
            desc = f"Each element is computed by the formula: {self.pattern_desc}"
        
        self.solution_steps.append(template.format(step=1, pattern_description=desc))
        
        self.final_answer = str(self.next_term)
    
    def _solve_series_sum(self, templates):
        """Сумма ряда."""
        misc = PROMPT_TEMPLATES.get("sequence", {}).get("misc", {})
        
        if self.series_type == "arithmetic":
            result = self.n * (self.n + 1) // 2
            step = misc.get("sum_arithmetic", {}).get(self.language, "")
            self.solution_steps.append(step.format(n=self.n, n_plus_1=self.n+1, result=result))
        else:  # squares
            result = self.n * (self.n + 1) * (2 * self.n + 1) // 6
            step = misc.get("sum_squares", {}).get(self.language, "")
            self.solution_steps.append(step.format(result=result))
        
        self.final_answer = str(result)
    
    def get_task_type(self) -> str:
        return "sequence"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу на последовательности."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
