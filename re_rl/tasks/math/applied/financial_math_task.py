# re_rl/tasks/financial_math_task.py

"""
FinancialMathTask — задачи по финансовой математике.

Поддерживаемые типы:
- simple_interest: простые проценты
- compound_interest: сложные проценты
- present_value: текущая стоимость
- annuity_pv: текущая стоимость аннуитета
- annuity_fv: будущая стоимость аннуитета
- loan_payment: платёж по кредиту
- npv: чистая приведённая стоимость
"""

import random
import math
from typing import List, Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class FinancialMathTask(BaseMathTask):
    """Генератор задач по финансовой математике."""
    
    TASK_TYPES = [
        "simple_interest", "compound_interest", "present_value",
        "annuity_pv", "annuity_fv", "loan_payment", "npv"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_principal": 1000, "max_rate": 5, "max_years": 2, "max_periods": 3},
        2: {"max_principal": 5000, "max_rate": 8, "max_years": 3, "max_periods": 4},
        3: {"max_principal": 10000, "max_rate": 10, "max_years": 5, "max_periods": 5},
        4: {"max_principal": 20000, "max_rate": 12, "max_years": 5, "max_periods": 5},
        5: {"max_principal": 50000, "max_rate": 15, "max_years": 10, "max_periods": 6},
        6: {"max_principal": 100000, "max_rate": 15, "max_years": 10, "max_periods": 7},
        7: {"max_principal": 200000, "max_rate": 18, "max_years": 15, "max_periods": 8},
        8: {"max_principal": 500000, "max_rate": 20, "max_years": 20, "max_periods": 10},
        9: {"max_principal": 1000000, "max_rate": 25, "max_years": 25, "max_periods": 10},
        10: {"max_principal": 1000000, "max_rate": 30, "max_years": 30, "max_periods": 12},
    }
    
    def __init__(
        self,
        task_type: str = "simple_interest",
        principal: float = None,
        rate: float = None,
        time: int = None,
        compounding: int = None,
        payment: float = None,
        cash_flows: List[float] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        **kwargs
    ):
        self.task_type = task_type.lower()
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        # Получаем параметры сложности
        preset = self._interpolate_difficulty(difficulty)
        self.max_principal = preset.get("max_principal", 50000)
        self.max_rate = preset.get("max_rate", 15)
        self.max_years = preset.get("max_years", 10)
        self.max_periods = preset.get("max_periods", 6)
        
        # Генерируем параметры
        self.principal = principal if principal is not None else self._random_principal()
        self.rate = rate if rate is not None else random.randint(1, self.max_rate)
        self.time = time if time is not None else random.randint(1, self.max_years)
        self.compounding = compounding if compounding is not None else random.choice([1, 2, 4, 12])
        self.payment = payment if payment is not None else random.randint(100, 5000)
        self.cash_flows = cash_flows if cash_flows else self._generate_cash_flows()
        
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _random_principal(self) -> int:
        """Генерирует округлённую сумму."""
        base = random.randint(1, self.max_principal // 1000) * 1000
        return base
    
    def _generate_cash_flows(self) -> List[float]:
        """Генерирует денежные потоки для NPV."""
        n = random.randint(3, min(6, self.max_periods))
        return [random.randint(1000, 20000) for _ in range(n)]
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("financial_math", {}).get("problem", {})
        
        if self.task_type == "simple_interest":
            template = templates.get("simple_interest", {}).get(self.language, "")
            return template.format(P=self.principal, r=self.rate, t=self.time)
        
        elif self.task_type == "compound_interest":
            template = templates.get("compound_interest", {}).get(self.language, "")
            return template.format(P=self.principal, r=self.rate, t=self.time, n=self.compounding)
        
        elif self.task_type == "present_value":
            # Вычисляем будущую стоимость для задачи
            fv = self.principal * (1 + self.rate / 100) ** self.time
            template = templates.get("present_value", {}).get(self.language, "")
            return template.format(FV=f"{fv:.2f}", t=self.time, r=self.rate)
        
        elif self.task_type == "annuity_pv":
            template = templates.get("annuity_pv", {}).get(self.language, "")
            return template.format(PMT=self.payment, n=self.time, r=self.rate)
        
        elif self.task_type == "annuity_fv":
            template = templates.get("annuity_fv", {}).get(self.language, "")
            return template.format(PMT=self.payment, n=self.time, r=self.rate)
        
        elif self.task_type == "loan_payment":
            template = templates.get("loan_payment", {}).get(self.language, "")
            return template.format(P=self.principal, t=self.time, r=self.rate)
        
        elif self.task_type == "npv":
            template = templates.get("npv", {}).get(self.language, "")
            return template.format(
                I0=self.principal, cash_flows=self.cash_flows, r=self.rate
            )
        
        return ""
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("financial_math", {}).get("steps", {})
        
        if self.task_type == "simple_interest":
            self._solve_simple_interest(templates)
        elif self.task_type == "compound_interest":
            self._solve_compound_interest(templates)
        elif self.task_type == "present_value":
            self._solve_present_value(templates)
        elif self.task_type == "annuity_pv":
            self._solve_annuity_pv(templates)
        elif self.task_type == "annuity_fv":
            self._solve_annuity_fv(templates)
        elif self.task_type == "loan_payment":
            self._solve_loan_payment(templates)
        elif self.task_type == "npv":
            self._solve_npv(templates)
        
    
    def _solve_simple_interest(self, templates):
        """Простые проценты."""
        r = self.rate / 100
        interest = self.principal * r * self.time
        total = self.principal + interest
        
        step1 = templates.get("simple_interest_formula", {}).get(self.language, "")
        self.solution_steps.append(step1.format(
            P=self.principal, r=r, t=self.time, I=f"{interest:.2f}"
        ))
        
        step2 = templates.get("simple_interest_total", {}).get(self.language, "")
        self.solution_steps.append(step2.format(
            P=self.principal, I=f"{interest:.2f}", A=f"{total:.2f}"
        ))
        
        self.final_answer = f"{total:.2f}"
    
    def _solve_compound_interest(self, templates):
        """Сложные проценты."""
        r = self.rate / 100
        n = self.compounding
        t = self.time
        
        amount = self.principal * (1 + r / n) ** (n * t)
        interest = amount - self.principal
        
        step1 = templates.get("compound_formula", {}).get(self.language, "")
        self.solution_steps.append(step1.format(P=self.principal, r=r, n=n, t=t))
        
        step2 = templates.get("compound_result", {}).get(self.language, "")
        self.solution_steps.append(step2.format(A=f"{amount:.2f}", interest=f"{interest:.2f}"))
        
        self.final_answer = f"{amount:.2f}"
    
    def _solve_present_value(self, templates):
        """Текущая стоимость."""
        r = self.rate / 100
        fv = self.principal * (1 + r) ** self.time
        pv = fv / (1 + r) ** self.time
        
        step = templates.get("pv_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(
            FV=f"{fv:.2f}", r=r, t=self.time, PV=f"{pv:.2f}"
        ))
        
        self.final_answer = f"{pv:.2f}"
    
    def _solve_annuity_pv(self, templates):
        """Текущая стоимость аннуитета."""
        r = self.rate / 100
        n = self.time
        
        if r == 0:
            pv = self.payment * n
        else:
            pv = self.payment * (1 - (1 + r) ** (-n)) / r
        
        step = templates.get("annuity_pv_formula", {}).get(self.language, "")
        self.solution_steps.append(step.format(
            PMT=self.payment, r=r, n=n, PV=f"{pv:.2f}"
        ))
        
        self.final_answer = f"{pv:.2f}"
    
    def _solve_annuity_fv(self, templates):
        """Будущая стоимость аннуитета."""
        r = self.rate / 100
        n = self.time
        
        if r == 0:
            fv = self.payment * n
        else:
            fv = self.payment * ((1 + r) ** n - 1) / r
        
        self.solution_steps.append(f"FV = PMT × [((1+r)^n - 1) / r] = {fv:.2f}")
        
        self.final_answer = f"{fv:.2f}"
    
    def _solve_loan_payment(self, templates):
        """Ежемесячный платёж по кредиту."""
        annual_rate = self.rate / 100
        monthly_rate = annual_rate / 12
        n = self.time * 12  # Количество месяцев
        
        if monthly_rate == 0:
            pmt = self.principal / n
        else:
            pmt = self.principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
        
        step = templates.get("loan_formula", {}).get(self.language, "")
        self.solution_steps.append(step)
        self.solution_steps.append(f"PMT = {pmt:.2f}")
        
        self.final_answer = f"{pmt:.2f}"
    
    def _solve_npv(self, templates):
        """Чистая приведённая стоимость."""
        r = self.rate / 100
        
        step1 = templates.get("npv_formula", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        pv_sum = 0
        for t, cf in enumerate(self.cash_flows, 1):
            pv = cf / (1 + r) ** t
            pv_sum += pv
            
            step = templates.get("npv_calculation", {}).get(self.language, "")
            self.solution_steps.append(step.format(step=t+1, t=t, cf=cf, r=r, pv=f"{pv:.2f}"))
        
        npv = -self.principal + pv_sum
        
        self.final_answer = f"NPV = {npv:.2f}"
    
    def get_task_type(self) -> str:
        return "financial_math"
    
    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False
    ):
        """Генерирует случайную задачу по финансовой математике."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode
        )
