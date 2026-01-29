# re_rl/tasks/number_theory_task.py

"""
NumberTheoryTask — задачи по теории чисел.

Поддерживаемые типы:
- gcd_lcm: НОД и НОК
- prime_factorization: разложение на простые множители
- modular_arithmetic: вычисления по модулю
- chinese_remainder: китайская теорема об остатках
- divisibility: проверка делимости
- diophantine: диофантовы уравнения
- euler_totient: функция Эйлера
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple, ClassVar
from dataclasses import dataclass

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class NumberTheoryTask(BaseMathTask):
    """Задачи по теории чисел."""
    
    TASK_TYPES = [
        "gcd_lcm", "prime_factorization", "modular_arithmetic",
        "chinese_remainder", "divisibility", "diophantine", "euler_totient"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_value": 20, "num_congruences": 2},
        2: {"max_value": 50, "num_congruences": 2},
        3: {"max_value": 100, "num_congruences": 2},
        4: {"max_value": 200, "num_congruences": 2},
        5: {"max_value": 500, "num_congruences": 3},
        6: {"max_value": 1000, "num_congruences": 3},
        7: {"max_value": 2000, "num_congruences": 3},
        8: {"max_value": 5000, "num_congruences": 4},
        9: {"max_value": 10000, "num_congruences": 4},
        10: {"max_value": 50000, "num_congruences": 5},
    }
    
    def __init__(
        self,
        task_type: str = "gcd_lcm",
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
        self.max_value = kwargs.get("max_value", preset.get("max_value", 100))
        self.num_congruences = kwargs.get("num_congruences", preset.get("num_congruences", 2))
        
        # Генерируем параметры задачи
        self._generate_task_params()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
    
    def _generate_task_params(self):
        """Генерирует параметры в зависимости от типа задачи."""
        if self.task_type == "gcd_lcm":
            self.a = self.kwargs.get("a", random.randint(2, self.max_value))
            self.b = self.kwargs.get("b", random.randint(2, self.max_value))
        
        elif self.task_type == "prime_factorization":
            self.n = self.kwargs.get("n", random.randint(2, self.max_value))
        
        elif self.task_type == "modular_arithmetic":
            self.a = self.kwargs.get("a", random.randint(2, min(20, self.max_value)))
            self.b = self.kwargs.get("b", random.randint(2, min(50, self.max_value)))
            self.m = self.kwargs.get("m", random.randint(3, min(100, self.max_value)))
        
        elif self.task_type == "chinese_remainder":
            self._generate_crt_params()
        
        elif self.task_type == "divisibility":
            self.n = self.kwargs.get("n", random.randint(10, self.max_value))
            self.d = self.kwargs.get("d", random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))
        
        elif self.task_type == "diophantine":
            self._generate_diophantine_params()
        
        elif self.task_type == "euler_totient":
            self.n = self.kwargs.get("n", random.randint(2, min(1000, self.max_value)))
    
    def _generate_crt_params(self):
        """Генерирует параметры для китайской теоремы об остатках."""
        # Выбираем взаимно простые модули
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
        selected_primes = random.sample(primes[:self.num_congruences + 2], self.num_congruences)
        
        self.congruences = []
        for m in selected_primes:
            a = random.randint(0, m - 1)
            self.congruences.append((a, m))
    
    def _generate_diophantine_params(self):
        """Генерирует параметры для диофантова уравнения ax + by = c."""
        # Генерируем a и b, затем c кратное их НОД
        self.a = random.randint(2, min(50, self.max_value))
        self.b = random.randint(2, min(50, self.max_value))
        gcd_ab = math.gcd(self.a, self.b)
        multiplier = random.randint(1, 10)
        self.c = gcd_ab * multiplier
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("number_theory", {}).get("problem", {})
        
        if self.task_type == "gcd_lcm":
            template = templates.get("gcd_lcm", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b)
        
        elif self.task_type == "prime_factorization":
            template = templates.get("prime_factorization", {}).get(self.language, "")
            return template.format(n=self.n)
        
        elif self.task_type == "modular_arithmetic":
            template = templates.get("modular_arithmetic", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, m=self.m)
        
        elif self.task_type == "chinese_remainder":
            template = templates.get("chinese_remainder", {}).get(self.language, "")
            if self.language == "ru":
                eqs = "\n".join([f"x ≡ {a} (mod {m})" for a, m in self.congruences])
            else:
                eqs = "\n".join([f"x ≡ {a} (mod {m})" for a, m in self.congruences])
            return template.format(equations=eqs)
        
        elif self.task_type == "divisibility":
            template = templates.get("divisibility", {}).get(self.language, "")
            return template.format(n=self.n, d=self.d)
        
        elif self.task_type == "diophantine":
            template = templates.get("diophantine", {}).get(self.language, "")
            return template.format(a=self.a, b=self.b, c=self.c)
        
        elif self.task_type == "euler_totient":
            template = templates.get("euler_totient", {}).get(self.language, "")
            return template.format(n=self.n)
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        steps_templates = PROMPT_TEMPLATES.get("number_theory", {}).get("steps", {})
        
        if self.task_type == "gcd_lcm":
            self._solve_gcd_lcm(steps_templates)
        elif self.task_type == "prime_factorization":
            self._solve_prime_factorization(steps_templates)
        elif self.task_type == "modular_arithmetic":
            self._solve_modular_arithmetic(steps_templates)
        elif self.task_type == "chinese_remainder":
            self._solve_chinese_remainder(steps_templates)
        elif self.task_type == "divisibility":
            self._solve_divisibility(steps_templates)
        elif self.task_type == "diophantine":
            self._solve_diophantine(steps_templates)
        elif self.task_type == "euler_totient":
            self._solve_euler_totient(steps_templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]
    
    def _solve_gcd_lcm(self, templates):
        """Решает задачу на НОД и НОК."""
        a, b = self.a, self.b
        original_a, original_b = a, b
        
        step = 1
        # Алгоритм Евклида
        while b != 0:
            q, r = divmod(a, b)
            step_template = templates.get("gcd_euclidean", {}).get(self.language, "")
            self.solution_steps.append(step_template.format(step=step, a=a, b=b, q=q, r=r))
            a, b = b, r
            step += 1
        
        gcd_val = a
        lcm_val = (original_a * original_b) // gcd_val
        
        # НОД
        gcd_template = templates.get("gcd_found", {}).get(self.language, "")
        self.solution_steps.append(gcd_template.format(a=original_a, b=original_b, gcd=gcd_val))
        
        # НОК
        lcm_template = templates.get("lcm_formula", {}).get(self.language, "")
        self.solution_steps.append(lcm_template.format(a=original_a, b=original_b, lcm=lcm_val))
        
        self.final_answer = f"НОД = {gcd_val}, НОК = {lcm_val}" if self.language == "ru" else f"GCD = {gcd_val}, LCM = {lcm_val}"
    
    def _solve_prime_factorization(self, templates):
        """Разложение на простые множители."""
        n = self.n
        original_n = n
        factors = []
        d = 2
        step = 1
        
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                quotient = n // d
                step_template = templates.get("factor_found", {}).get(self.language, "")
                self.solution_steps.append(step_template.format(step=step, n=n, factor=d, quotient=quotient))
                n = quotient
                step += 1
            d += 1
        
        if n > 1:
            factors.append(n)
            step_template = templates.get("factor_found", {}).get(self.language, "")
            self.solution_steps.append(step_template.format(step=step, n=n, factor=n, quotient=1))
        
        # Формируем строку разложения
        factor_counts = {}
        for f in factors:
            factor_counts[f] = factor_counts.get(f, 0) + 1
        
        factorization_str = " × ".join(
            f"{p}^{e}" if e > 1 else str(p) 
            for p, e in sorted(factor_counts.items())
        )
        
        result_template = templates.get("factorization_result", {}).get(self.language, "")
        self.solution_steps.append(result_template.format(n=original_n, factorization=factorization_str))
        
        self.final_answer = factorization_str
    
    def _solve_modular_arithmetic(self, templates):
        """Вычисление a^b mod m."""
        result = pow(self.a, self.b, self.m)
        
        # Показываем несколько шагов быстрого возведения в степень
        step = 1
        base = self.a % self.m
        exp = self.b
        current = 1
        
        while exp > 0:
            if exp % 2 == 1:
                current = (current * base) % self.m
            step_template = templates.get("mod_exp_step", {}).get(self.language, "")
            self.solution_steps.append(step_template.format(
                step=step, base=self.a, exp=exp, result=current, m=self.m
            ))
            base = (base * base) % self.m
            exp //= 2
            step += 1
            if step > 10:  # Ограничиваем количество шагов
                break
        
        self.final_answer = str(result)
    
    def _solve_chinese_remainder(self, templates):
        """Китайская теорема об остатках."""
        # Вычисляем M = произведение всех модулей
        M = 1
        for _, m in self.congruences:
            M *= m
        
        result = 0
        step = 1
        
        for a, m in self.congruences:
            M_i = M // m
            # Находим обратный элемент M_i по модулю m
            y_i = pow(M_i, -1, m)
            result += a * M_i * y_i
            
            step_template = templates.get("crt_step", {}).get(self.language, "")
            self.solution_steps.append(step_template.format(
                step=step, a=a, m=m, M_i=M_i, y_i=y_i
            ))
            step += 1
        
        result = result % M
        self.final_answer = f"x ≡ {result} (mod {M})"
    
    def _solve_divisibility(self, templates):
        """Проверка делимости."""
        is_divisible = self.n % self.d == 0
        quotient = self.n // self.d
        remainder = self.n % self.d
        
        answers = PROMPT_TEMPLATES.get("number_theory", {}).get("answers", {})
        
        if is_divisible:
            step1 = templates.get("divisibility_divide", {}).get(self.language, "")
            self.solution_steps.append(step1.format(n=self.n, d=self.d, quotient=quotient))
            
            step2 = templates.get("divisibility_yes", {}).get(self.language, "")
            self.solution_steps.append(step2.format(n=self.n, d=self.d))
            
            answer_template = answers.get("divisible_yes", {}).get(self.language, "")
            self.final_answer = answer_template.format(n=self.n, d=self.d)
        else:
            step1 = templates.get("divisibility_remainder", {}).get(self.language, "")
            self.solution_steps.append(step1.format(n=self.n, d=self.d, quotient=quotient, remainder=remainder))
            
            step2 = templates.get("divisibility_no", {}).get(self.language, "")
            self.solution_steps.append(step2.format(n=self.n, d=self.d, remainder=remainder))
            
            answer_template = answers.get("divisible_no", {}).get(self.language, "")
            self.final_answer = answer_template.format(remainder=remainder)
    
    def _solve_diophantine(self, templates):
        """Решение диофантова уравнения ax + by = c."""
        gcd_ab = math.gcd(self.a, self.b)
        
        # Шаг 1: Проверяем разрешимость
        gcd_template = templates.get("diophantine_gcd", {}).get(self.language, "")
        self.solution_steps.append(gcd_template.format(a=self.a, b=self.b, gcd=gcd_ab, c=self.c))
        
        # Находим частное решение с помощью расширенного алгоритма Евклида
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        _, x0, y0 = extended_gcd(self.a, self.b)
        multiplier = self.c // gcd_ab
        x0 *= multiplier
        y0 *= multiplier
        
        # Шаг 2: Частное решение
        particular_template = templates.get("diophantine_particular", {}).get(self.language, "")
        self.solution_steps.append(particular_template.format(x0=x0, y0=y0))
        
        # Шаг 3: Общее решение
        b_div = self.b // gcd_ab
        a_div = self.a // gcd_ab
        general_template = templates.get("diophantine_general", {}).get(self.language, "")
        self.solution_steps.append(general_template.format(x0=x0, y0=y0, b_div=b_div, a_div=a_div))
        
        if self.language == "ru":
            self.final_answer = f"x = {x0} + {b_div}t, y = {y0} - {a_div}t, t ∈ ℤ"
        else:
            self.final_answer = f"x = {x0} + {b_div}t, y = {y0} - {a_div}t, t ∈ ℤ"
    
    def _solve_euler_totient(self, templates):
        """Вычисление функции Эйлера φ(n)."""
        n = self.n
        original_n = n
        
        # Разложение на простые множители
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        
        # Шаг 1: Разложение
        factorization_str = " × ".join(
            f"{p}^{e}" if e > 1 else str(p) 
            for p, e in sorted(factors.items())
        )
        factor_template = templates.get("euler_factorize", {}).get(self.language, "")
        self.solution_steps.append(factor_template.format(n=original_n, factorization=factorization_str))
        
        # Шаг 2: Вычисление φ(n) = n × ∏(1 - 1/p)
        result = original_n
        product_terms = []
        for p in factors:
            result = result * (p - 1) // p
            product_terms.append(f"(1 - 1/{p})")
        
        formula_template = templates.get("euler_formula", {}).get(self.language, "")
        self.solution_steps.append(formula_template.format(
            n=original_n, product_terms=" × ".join(product_terms), result=result
        ))
        
        self.final_answer = str(result)
    
    def get_task_type(self) -> str:
        return "number_theory"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5
    ):
        """Генерирует случайную задачу по теории чисел."""
        if task_type is None:
            task_type = random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty
        )
