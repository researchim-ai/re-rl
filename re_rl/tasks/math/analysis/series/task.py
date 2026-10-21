# re_rl/tasks/series_task.py

"""
SeriesTask — задачи на ряды и сходимость.

Поддерживаемые типы:
- geometric_sum: сумма геометрического ряда
- convergence_test: исследование сходимости
- partial_sum: частичная сумма
- taylor_series: ряд Тейлора
- telescoping: телескопический ряд
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
import math
from typing import List, Dict, Any, ClassVar
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class SeriesTask(BaseMathTask):
    """Генератор задач на ряды и сходимость."""
    
    TASK_TYPES = [
        "geometric_sum", "convergence_test", "partial_sum", "telescoping"
    ]
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {texts.literal('literals.s0'): 5, "simple_ratio": True, "max_n": 5},
        2: {texts.literal('literals.s1'): 10, "simple_ratio": True, "max_n": 10},
        3: {texts.literal('literals.s2'): 10, "simple_ratio": False, "max_n": 15},
        4: {texts.literal('literals.s3'): 20, "simple_ratio": False, "max_n": 20},
        5: {texts.literal('literals.s4'): 20, "simple_ratio": False, "max_n": 25},
        6: {texts.literal('literals.s5'): 50, "simple_ratio": False, "max_n": 30},
        7: {texts.literal('literals.s6'): 50, "simple_ratio": False, "max_n": 40},
        8: {texts.literal('literals.s7'): 100, "simple_ratio": False, "max_n": 50},
        9: {texts.literal('literals.s8'): 100, "simple_ratio": False, "max_n": 75},
        10: {texts.literal('literals.s9'): 100, "simple_ratio": False, "max_n": 100},
    }
    
    def __init__(
        self,
        task_type: str = "geometric_sum",
        first_term: float = None,
        ratio: float = None,
        n_terms: int = None,
        series_type: str = None,
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
        self.max_first_term = preset.get(texts.t('s10', language), 20)
        self.simple_ratio = preset.get("simple_ratio", False)
        self.max_n = preset.get("max_n", 25)
        
        # Генерируем параметры
        self.first_term = first_term if first_term is not None else random.randint(1, self.max_first_term)
        self.ratio = ratio if ratio is not None else self._generate_ratio()
        self.n_terms = n_terms if n_terms is not None else random.randint(5, min(20, self.max_n))
        self.series_type = series_type or random.choice(["p_series", "harmonic", "geometric", "ratio_test"])
        
        # Параметры для разных типов рядов
        self._generate_series_params()
        
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode
    
    def _generate_ratio(self) -> float:
        """Генерирует отношение для геометрического ряда."""
        if self.simple_ratio:
            return random.choice([0.5, 0.25, 1/3, 2/3])
        else:
            # Генерируем |r| < 1 для сходимости
            return round(random.uniform(0.1, 0.9), 2)
    
    def _generate_series_params(self):
        """Генерирует параметры для разных типов рядов."""
        if self.task_type == "convergence_test":
            # Генерируем ряд для проверки сходимости
            self.p = random.choice([0.5, 1, 1.5, 2, 3])  # для p-ряда
            self.base = random.randint(2, 5)  # для геометрического
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        is_latex = self._output_format == "latex"
        templates = PROMPT_TEMPLATES.get("series", {}).get("problem", {})
        
        # Форматируем выражение ряда
        if self.task_type == "geometric_sum":
            second_term = self.first_term * self.ratio
            if is_latex:
                series_expr = f"${self.first_term} + {second_term:.4g} + ...$"
            else:
                series_expr = f"{self.first_term} + {second_term:.4g} + ..."
        
        elif self.task_type == "convergence_test":
            if self.series_type == "p_series":
                if is_latex:
                    series_expr = texts.t('s14', self.language, p=self.p)
                else:
                    series_expr = f"Σ(1/n^{self.p}), n = 1, 2, 3, ..."
            elif self.series_type == "harmonic":
                if is_latex:
                    series_expr = texts.literal('literals.s16')
                else:
                    series_expr = f"Σ(1/n), n = 1, 2, 3, ..."
            elif self.series_type == "geometric":
                if is_latex:
                    series_expr = texts.t('s19', self.language, ratio=self.ratio)
                else:
                    series_expr = f"Σ(({self.ratio})^n), n = 1, 2, 3, ..."
            else:  # ratio_test
                if is_latex:
                    series_expr = texts.t('s20', self.language, base=self.base)
                else:
                    series_expr = f"Σ(n!/{self.base}^n), n = 1, 2, 3, ..."
        
        elif self.task_type == "partial_sum":
            if is_latex:
                series_expr = f"$S_{{{self.n_terms}}} = \\sum_{{k=1}}^{{{self.n_terms}}} {self.first_term} \\cdot {self.ratio}^{{k-1}}$"
            else:
                series_expr = f"S_{self.n_terms} = Σ({self.first_term}·{self.ratio}^(k-1)), k = 1..{self.n_terms}"
        
        elif self.task_type == "telescoping":
            if is_latex:
                series_expr = texts.literal('literals.s17')
            else:
                series_expr = texts.t('s18', self.language)
        else:
            series_expr = ""
        
        # Используем шаблоны
        template = templates.get(self.task_type, {}).get(self.language, "")
        return template.format(series_expression=series_expr)
    
    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("series", {}).get("steps", {})
        conclusions = PROMPT_TEMPLATES.get("series", {}).get("conclusions", {})
        
        if self.task_type == "geometric_sum":
            self._solve_geometric_sum(templates)
        elif self.task_type == "convergence_test":
            self._solve_convergence_test(templates, conclusions)
        elif self.task_type == "partial_sum":
            self._solve_partial_sum(templates)
        elif self.task_type == "telescoping":
            self._solve_telescoping(templates)
        
    
    def _solve_geometric_sum(self, templates):
        """Сумма бесконечного геометрического ряда."""
        a = self.first_term
        r = self.ratio
        
        # Шаг 1: Определяем тип
        step1 = templates.get("identify_type", {}).get(self.language, "")
        type_name = get_template(PROMPT_TEMPLATES["inline"], texts.t('s11', self.language), self.language, augment=False)
        self.solution_steps.append(step1.format(type=type_name))
        
        # Шаг 2: Находим отношение
        second_term = a * r
        step2 = templates.get("geometric_ratio", {}).get(self.language, "")
        self.solution_steps.append(step2.format(step=2, second=second_term, first=a, ratio=r))
        
        # Шаг 3: Применяем формулу суммы
        if abs(r) < 1:
            sum_value = a / (1 - r)
            step3 = templates.get(texts.t('s15', self.language), {}).get(self.language, "")
            self.solution_steps.append(step3.format(step=3, a=a, r=r, sum=f"{sum_value:.4f}"))
            self.final_answer = f"S = {sum_value:.4f}"
        else:
            self.final_answer = get_template(PROMPT_TEMPLATES["inline"], texts.t('s13', self.language), self.language, augment=False)
    
    def _solve_convergence_test(self, templates, conclusions):
        """Исследование сходимости."""
        if self.series_type == "p_series":
            # p-ряд сходится при p > 1
            converges = self.p > 1
            
            step = templates.get("identify_type", {}).get(self.language, "")
            self.solution_steps.append(step.format(type=f"p-series (p = {self.p})"))
            
            comparison = ">" if self.p > 1 else ("=" if self.p == 1 else "<")
            conclusion = conclusions.get("converges" if converges else "diverges", {}).get(self.language, "")
            
            step2 = templates.get("ratio_conclusion", {}).get(self.language, "")
            self.solution_steps.append(step2.format(step=2, limit=self.p, comparison=comparison, conclusion=conclusion))
            
        elif self.series_type == "harmonic":
            # Гармонический ряд расходится
            step = templates.get("identify_type", {}).get(self.language, "")
            self.solution_steps.append(step.format(type="harmonic"))
            
            conclusion = conclusions.get("diverges", {}).get(self.language, "")
            self.solution_steps.append(f"p = 1: {conclusion}")
            converges = False
            
        elif self.series_type == "geometric":
            # Геометрический ряд
            converges = abs(self.ratio) < 1
            
            step = templates.get("identify_type", {}).get(self.language, "")
            self.solution_steps.append(step.format(type="geometric"))
            
            conclusion = conclusions.get("converges" if converges else "diverges", {}).get(self.language, "")
            self.solution_steps.append(f"|r| = {abs(self.ratio)}: {conclusion}")
            
        else:  # ratio_test
            # Признак Даламбера для n!/base^n
            # lim |a_{n+1}/a_n| = lim |(n+1)!/base^{n+1} * base^n/n!| = lim (n+1)/base = ∞
            
            step = templates.get("ratio_test", {}).get(self.language, "")
            self.solution_steps.append(step.format(step=1, limit="∞"))
            
            conclusion = conclusions.get("diverges", {}).get(self.language, "")
            step2 = templates.get("ratio_conclusion", {}).get(self.language, "")
            self.solution_steps.append(step2.format(step=2, limit="∞", comparison=">", conclusion=conclusion))
            converges = False
        
        conv_str = conclusions.get("converges" if converges else "diverges", {}).get(self.language, "")
        self.final_answer = conv_str
    
    def _solve_partial_sum(self, templates):
        """Частичная сумма геометрического ряда."""
        a = self.first_term
        r = self.ratio
        n = self.n_terms
        
        # S_n = a(1 - r^n) / (1 - r)
        if r != 1:
            partial_sum = a * (1 - r ** n) / (1 - r)
        else:
            partial_sum = a * n
        
        step = templates.get("identify_type", {}).get(self.language, "")
        self.solution_steps.append(step.format(type="geometric"))
        
        self.solution_steps.append(f"S_{n} = {a}(1 - {r}^{n}) / (1 - {r}) = {partial_sum:.4f}")
        
        self.final_answer = f"S_{n} = {partial_sum:.4f}"
    
    def _solve_telescoping(self, templates):
        """Телескопический ряд Σ 1/(n(n+1))."""
        # 1/(n(n+1)) = 1/n - 1/(n+1)
        # Сумма = (1 - 1/2) + (1/2 - 1/3) + ... = 1 - lim 1/(n+1) = 1
        
        step = templates.get("identify_type", {}).get(self.language, "")
        type_name = get_template(PROMPT_TEMPLATES["inline"], texts.t('s12', self.language), self.language, augment=False)
        self.solution_steps.append(step.format(type=type_name))
        
        decomposition = "1/(n(n+1)) = 1/n - 1/(n+1)"
        self.solution_steps.append(f"Partial fractions: {decomposition}")
        
        self.solution_steps.append("S = (1 - 1/2) + (1/2 - 1/3) + ... = 1 - lim(1/(n+1)) = 1")
        
        self.final_answer = "S = 1"
    
    def get_task_type(self) -> str:
        return "series"
    
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
        """Генерирует случайную задачу на ряды."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            output_format=output_format,
            reasoning_mode=reasoning_mode
        )
