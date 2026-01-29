# re_rl/tasks/category_theory_task.py

"""
CategoryTheoryTask — задачи по теории категорий.

Поддерживаемые типы:
- morphism_composition: композиция морфизмов
- commutative_diagram: коммутативность диаграммы
"""

import random
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import List, Dict, Any


class CategoryTheoryTask(BaseMathTask):
    """
    Генератор задач по теории категорий.
    
    Параметры:
    - task_type: "morphism_composition", "commutative_diagram"
    - category_type: "set", "group", "topology" (пока не используется)
    """
    
    TASK_TYPES = ["morphism_composition", "commutative_diagram"]
    
    def __init__(
        self,
        task_type: str = "morphism_composition",
        category_type: str = "set",
        language: str = "ru",
        detail_level: int = 3,
        output_format: str = "text"
    ):
        self.task_type = task_type.lower()
        self.category_type = category_type.lower()
        self.objects: List[str] = []
        self.morphisms: List[Dict[str, Any]] = []
        self.is_commutative: bool = False
        self._output_format = output_format
        
        # Генерируем данные задачи
        self._generate_task_data()
        
        # Создаём описание
        self.language = language.lower()  # Fix: set before _create_problem_description
        description = self._create_problem_description()
        super().__init__(description, language, detail_level, output_format)

    def _generate_task_data(self):
        """Генерирует объекты и морфизмы."""
        if self.task_type == "morphism_composition":
            self._generate_composition_problem()
        elif self.task_type == "commutative_diagram":
            self._generate_diagram_problem()

    def _generate_composition_problem(self):
        """Генерирует задачу на композицию."""
        self.objects = ["A", "B", "C", "D"]
        self.morphisms = [
            {'name': 'f', 'source': 'A', 'target': 'B'},
            {'name': 'g', 'source': 'B', 'target': 'C'},
            {'name': 'h', 'source': 'C', 'target': 'D'}
        ]

    def _generate_diagram_problem(self):
        """Генерирует задачу на коммутативную диаграмму."""
        self.objects = ["A", "B", "C", "D"]
        self.morphisms = [
            {'name': 'f', 'source': 'A', 'target': 'B'},
            {'name': 'g', 'source': 'A', 'target': 'C'},
            {'name': 'h', 'source': 'B', 'target': 'D'},
            {'name': 'k', 'source': 'C', 'target': 'D'}
        ]
        self.is_commutative = random.choice([True, False])

    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("category_theory", {}).get("problem", {})
        
        morphism_descs = "\n".join([
            f"{m['name']}: {m['source']} → {m['target']}"
            for m in self.morphisms
        ])
        
        if self.task_type == "morphism_composition":
            template = templates.get("morphism_composition", {}).get(self.language, "")
        else:
            template = templates.get("commutative_diagram", {}).get(self.language, "")
        
        return template.format(morphisms=morphism_descs)

    def solve(self):
        """Решает задачу пошагово."""
        self.solution_steps = []
        templates = PROMPT_TEMPLATES.get("category_theory", {}).get("steps", {})
        
        if self.task_type == "morphism_composition":
            self._solve_composition(templates)
        elif self.task_type == "commutative_diagram":
            self._solve_diagram(templates)
        
        # Ограничиваем по detail_level
        if len(self.solution_steps) > self.detail_level:
            self.solution_steps = self.solution_steps[:self.detail_level]

    def _solve_composition(self, templates):
        """Решает задачу на композицию морфизмов."""
        self.final_answer = "h ∘ g ∘ f: A → D"
        
        step1 = templates.get("identify_domains", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        step2 = templates.get("morphism_list", {}).get(self.language, "")
        self.solution_steps.append(step2)
        
        step3 = templates.get("apply_morphisms", {}).get(self.language, "")
        self.solution_steps.append(step3)
        
        step4 = templates.get("composition_result", {}).get(self.language, "")
        self.solution_steps.append(step4)
        
        final_template = PROMPT_TEMPLATES.get("category_theory", {}).get("final_answer", {}).get(self.language, "")
        self.solution_steps.append(final_template.format(answer=self.final_answer))

    def _solve_diagram(self, templates):
        """Решает задачу на коммутативную диаграмму."""
        if self.is_commutative:
            self.final_answer = "Да" if self.language == "ru" else "Yes"
            reason_key = "commutes"
        else:
            self.final_answer = "Нет" if self.language == "ru" else "No"
            reason_key = "not_commutes"
        
        step1 = templates.get("check_paths", {}).get(self.language, "")
        self.solution_steps.append(step1)
        
        step2 = templates.get("two_paths", {}).get(self.language, "")
        self.solution_steps.append(step2)
        
        reason = templates.get(reason_key, {}).get(self.language, "")
        self.solution_steps.append(reason)

    def get_task_type(self) -> str:
        return "category_theory"

    @classmethod
    def generate_random_task(
        cls,
        task_type: str = None,
        language: str = "ru",
        detail_level: int = 3
    ):
        """Генерирует случайную задачу по теории категорий."""
        task_type = task_type or random.choice(cls.TASK_TYPES)
        return cls(
            task_type=task_type,
            language=language,
            detail_level=detail_level
        )
