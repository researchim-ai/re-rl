# re_rl/tasks/combinatorics_task.py

"""
CombinatoricsTask — комбинаторные задачи.

Поддерживаемые типы:
- permutations: перестановки P(n)
- permutations_k: размещения P(n, k)
- combinations: сочетания C(n, k)
- combinations_repetition: сочетания с повторениями
- binomial: биномиальные коэффициенты
- multinomial: мультиномиальные коэффициенты
- pigeonhole: принцип Дирихле
- inclusion_exclusion: формула включения-исключения
- derangements: беспорядки
- stars_and_bars: шары и перегородки
- circular_permutation: круговые перестановки
"""

import random
import math
from typing import List, Dict, Any, Optional, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class CombinatoricsTask(BaseMathTask):
    """Комбинаторные задачи."""
    
    TASK_TYPES = [
        "permutations", "permutations_k", "combinations", "combinations_repetition",
        "binomial", "multinomial", "pigeonhole", "inclusion_exclusion",
        "derangements", "stars_and_bars", "circular_permutation"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_n": 5, "max_k": 3},
        2: {"max_n": 7, "max_k": 4},
        3: {"max_n": 10, "max_k": 5},
        4: {"max_n": 12, "max_k": 6},
        5: {"max_n": 15, "max_k": 7},
        6: {"max_n": 18, "max_k": 8},
        7: {"max_n": 20, "max_k": 10},
        8: {"max_n": 25, "max_k": 12},
        9: {"max_n": 30, "max_k": 15},
        10: {"max_n": 50, "max_k": 20},
    }
    
    def __init__(
        self,
        task_type: str = "combinations",
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
        self.max_n = kwargs.get("max_n", preset.get("max_n", 15))
        self.max_k = kwargs.get("max_k", preset.get("max_k", 7))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_task_params(self):
        """Генерирует параметры задачи."""
        if self.task_type == "permutations":
            self.n = self.kwargs.get("n", random.randint(3, min(10, self.max_n)))
        
        elif self.task_type == "permutations_k":
            self.n = self.kwargs.get("n", random.randint(4, self.max_n))
            self.k = self.kwargs.get("k", random.randint(2, min(self.n, self.max_k)))
        
        elif self.task_type == "combinations":
            self.n = self.kwargs.get("n", random.randint(4, self.max_n))
            self.k = self.kwargs.get("k", random.randint(1, min(self.n, self.max_k)))
        
        elif self.task_type == "combinations_repetition":
            self.n = self.kwargs.get("n", random.randint(3, min(10, self.max_n)))
            self.k = self.kwargs.get("k", random.randint(2, min(8, self.max_k)))
        
        elif self.task_type == "binomial":
            self.n = self.kwargs.get("n", random.randint(4, self.max_n))
            self.k = self.kwargs.get("k", random.randint(1, min(self.n, self.max_k)))
        
        elif self.task_type == "multinomial":
            self.n = self.kwargs.get("n", random.randint(6, min(15, self.max_n)))
            # Генерируем группы, сумма которых равна n
            num_groups = random.randint(2, 4)
            remaining = self.n
            self.groups = []
            for i in range(num_groups - 1):
                g = random.randint(1, remaining - (num_groups - i - 1))
                self.groups.append(g)
                remaining -= g
            self.groups.append(remaining)
        
        elif self.task_type == "pigeonhole":
            self.n = self.kwargs.get("n", random.randint(10, 50))
            self.k = self.kwargs.get("k", random.randint(3, 8))
            self.m = self.kwargs.get("m", random.randint(2, 5))
        
        elif self.task_type == "inclusion_exclusion":
            self.n = self.kwargs.get("n", random.randint(50, 200))
            self.divisors = self.kwargs.get("divisors", random.sample([2, 3, 5, 7], k=random.randint(2, 3)))
        
        elif self.task_type == "derangements":
            self.n = self.kwargs.get("n", random.randint(3, min(10, self.max_n)))
        
        elif self.task_type == "stars_and_bars":
            self.n = self.kwargs.get("n", random.randint(5, min(20, self.max_n)))
            self.k = self.kwargs.get("k", random.randint(2, min(6, self.max_k)))
        
        elif self.task_type == "circular_permutation":
            self.n = self.kwargs.get("n", random.randint(3, min(10, self.max_n)))
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("combinatorics", {}).get("problem", {})
        
        if self.task_type == "permutations":
            template = templates.get("permutations", {}).get(self.language, "")
            return template.format(n=self.n)
        
        elif self.task_type == "permutations_k":
            template = templates.get("permutations_k", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k)
        
        elif self.task_type == "combinations":
            template = templates.get("combinations", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k)
        
        elif self.task_type == "combinations_repetition":
            template = templates.get("combinations_repetition", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k)
        
        elif self.task_type == "binomial":
            template = templates.get("binomial", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k)
        
        elif self.task_type == "multinomial":
            template = templates.get("multinomial", {}).get(self.language, "")
            return template.format(n=self.n, groups=", ".join(map(str, self.groups)))
        
        elif self.task_type == "pigeonhole":
            template = templates.get("pigeonhole", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k, m=self.m)
        
        elif self.task_type == "inclusion_exclusion":
            template = templates.get("inclusion_exclusion", {}).get(self.language, "")
            return template.format(n=self.n, divisors=", ".join(map(str, self.divisors)))
        
        elif self.task_type == "derangements":
            template = templates.get("derangements", {}).get(self.language, "")
            return template.format(n=self.n)
        
        elif self.task_type == "stars_and_bars":
            template = templates.get("stars_and_bars", {}).get(self.language, "")
            return template.format(n=self.n, k=self.k)
        
        elif self.task_type == "circular_permutation":
            template = templates.get("circular_permutation", {}).get(self.language, "")
            return template.format(n=self.n)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("combinatorics", {}).get("steps", {})
        
        if self.task_type == "permutations":
            self._solve_permutations(steps_templates)
        elif self.task_type == "permutations_k":
            self._solve_permutations_k(steps_templates)
        elif self.task_type == "combinations":
            self._solve_combinations(steps_templates)
        elif self.task_type == "combinations_repetition":
            self._solve_combinations_repetition(steps_templates)
        elif self.task_type == "binomial":
            self._solve_binomial(steps_templates)
        elif self.task_type == "multinomial":
            self._solve_multinomial(steps_templates)
        elif self.task_type == "pigeonhole":
            self._solve_pigeonhole(steps_templates)
        elif self.task_type == "inclusion_exclusion":
            self._solve_inclusion_exclusion(steps_templates)
        elif self.task_type == "derangements":
            self._solve_derangements(steps_templates)
        elif self.task_type == "stars_and_bars":
            self._solve_stars_and_bars(steps_templates)
        elif self.task_type == "circular_permutation":
            self._solve_circular_permutation(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_permutations(self, templates):
        """P(n) = n!"""
        result = math.factorial(self.n)
        
        template = templates.get("factorial", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, result=result))
        
        self.final_answer = str(result)
    
    def _solve_permutations_k(self, templates):
        """P(n, k) = n! / (n-k)!"""
        result = math.perm(self.n, self.k)
        
        template = templates.get("permutation_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, k=self.k, result=result))
        
        self.final_answer = str(result)
    
    def _solve_combinations(self, templates):
        """C(n, k) = n! / (k! * (n-k)!)"""
        result = math.comb(self.n, self.k)
        
        template = templates.get("combination_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, k=self.k, result=result))
        
        self.final_answer = str(result)
    
    def _solve_combinations_repetition(self, templates):
        """C(n+k-1, k)"""
        n_plus_k_minus_1 = self.n + self.k - 1
        result = math.comb(n_plus_k_minus_1, self.k)
        
        template = templates.get("combination_rep_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, n=self.n, k=self.k, 
            n_plus_k_minus_1=n_plus_k_minus_1, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_binomial(self, templates):
        """C(n, k)"""
        result = math.comb(self.n, self.k)
        
        template = templates.get("combination_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, k=self.k, result=result))
        
        self.final_answer = str(result)
    
    def _solve_multinomial(self, templates):
        """n! / (k1! * k2! * ... * km!)"""
        numerator = math.factorial(self.n)
        denominator = 1
        for g in self.groups:
            denominator *= math.factorial(g)
        result = numerator // denominator
        
        factorials_str = " × ".join(f"{g}!" for g in self.groups)
        template = templates.get("multinomial_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, n=self.n, factorials=factorials_str, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_pigeonhole(self, templates):
        """По принципу Дирихле: (m-1) * k + 1"""
        result = (self.m - 1) * self.k + 1
        
        template = templates.get("pigeonhole_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, m=self.m, k=self.k, result=result))
        
        self.final_answer = str(result)
    
    def _solve_inclusion_exclusion(self, templates):
        """Формула включения-исключения."""
        from itertools import combinations as iter_combinations
        
        total = 0
        step = 1
        
        for r in range(1, len(self.divisors) + 1):
            for combo in iter_combinations(self.divisors, r):
                lcm_val = combo[0]
                for d in combo[1:]:
                    lcm_val = lcm_val * d // math.gcd(lcm_val, d)
                
                count = self.n // lcm_val
                sign = 1 if r % 2 == 1 else -1
                total += sign * count
                
                sets_str = ",".join(map(str, combo))
                template = templates.get("inclusion_exclusion_step", {}).get(self.language, "")
                if step <= 5:  # Ограничиваем количество шагов
                    self.solution_steps.append(template.format(step=step, sets=sets_str, count=count))
                step += 1
        
        self.final_answer = str(total)
    
    def _solve_derangements(self, templates):
        """D(n) = n! * sum((-1)^k / k!) для k от 0 до n"""
        result = 0
        factorial_n = math.factorial(self.n)
        
        for k in range(self.n + 1):
            result += ((-1) ** k) * factorial_n // math.factorial(k)
        
        template = templates.get("derangement_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, result=result))
        
        self.final_answer = str(result)
    
    def _solve_stars_and_bars(self, templates):
        """C(n + k - 1, k - 1)"""
        result = math.comb(self.n + self.k - 1, self.k - 1)
        
        template = templates.get("combination_rep_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(
            step=1, n=self.n, k=self.k - 1,
            n_plus_k_minus_1=self.n + self.k - 1, result=result
        ))
        
        self.final_answer = str(result)
    
    def _solve_circular_permutation(self, templates):
        """(n-1)!"""
        result = math.factorial(self.n - 1)
        
        template = templates.get("circular_formula", {}).get(self.language, "")
        self.solution_steps.append(template.format(step=1, n=self.n, result=result))
        
        self.final_answer = str(result)
    
    def get_task_type(self) -> str:
        return "combinatorics"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную комбинаторную задачу."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
