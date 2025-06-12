# re_rl/tasks/category_theory_task.py

import random
from re_rl.tasks.base_task import BaseMathTask
from typing import List, Dict, Any

class CategoryTheoryTask(BaseMathTask):
    """
    Генератор задач по теории категорий: композиция морфизмов, коммутативность диаграмм.
    Параметры:
    - task_type: "morphism_composition", "commutative_diagram"
    - category_type: "set", "group", "topology"  # NOTE: currently unused, tasks are abstract
    """
    def __init__(self, task_type="morphism_composition", category_type="set", 
                 language: str = "ru", detail_level: int = 3):
        self.task_type = task_type.lower()
        self.category_type = category_type.lower() # TODO: Implement concrete categories
        self.objects: List[str] = []
        self.morphisms: List[Dict[str, Any]] = []
        self.is_commutative: bool = False
        super().__init__("", language, detail_level)

    def generate_task_data(self):
        """Generates objects and morphisms based on the task type."""
        if self.task_type == "morphism_composition":
            self._generate_composition_problem()
        elif self.task_type == "commutative_diagram":
            self._generate_diagram_problem()

    def _generate_composition_problem(self):
        self.objects = ["A", "B", "C", "D"]
        self.morphisms = [
            {'name': 'f', 'source': 'A', 'target': 'B'},
            {'name': 'g', 'source': 'B', 'target': 'C'},
            {'name': 'h', 'source': 'C', 'target': 'D'}
        ]

    def _generate_diagram_problem(self):
        # Using a square diagram for more interest
        self.objects = ["A", "B", "C", "D"]
        self.morphisms = [
            {'name': 'f', 'source': 'A', 'target': 'B'},
            {'name': 'g', 'source': 'A', 'target': 'C'},
            {'name': 'h', 'source': 'B', 'target': 'D'},
            {'name': 'k', 'source': 'C', 'target': 'D'}
        ]
        self.is_commutative = random.choice([True, False])

    def _create_problem_description(self) -> str:
        self.generate_task_data()
        
        morphism_descs = "\n".join([f"{m['name']}: {m['source']} → {m['target']}" 
                                  for m in self.morphisms])

        if self.task_type == "morphism_composition":
            question_ru = "Даны морфизмы:\n{morphisms}\n\nНайдите композицию h ∘ g ∘ f."
            question_en = "Given the morphisms:\n{morphisms}\n\nFind the composition h ∘ g ∘ f."
            return question_ru.format(morphisms=morphism_descs) if self.language == "ru" else question_en.format(morphisms=morphism_descs)

        elif self.task_type == "commutative_diagram":
            question_ru = "Дана диаграмма морфизмов:\n{morphisms}\n\nКоммутирует ли эта диаграмма (т.е. верно ли, что h ∘ f = k ∘ g)?"
            question_en = "Given the diagram of morphisms:\n{morphisms}\n\nDoes this diagram commute (i.e., is it true that h ∘ f = k ∘ g)?"
            return question_ru.format(morphisms=morphism_descs) if self.language == "ru" else question_en.format(morphisms=morphism_descs)
        
        return "" # Should not happen

    def solve(self):
        self.description = self._create_problem_description()
        steps = []
        
        if self.task_type == "morphism_composition":
            # f: A -> B, g: B -> C, h: C -> D
            # composition h o g o f : A -> D
            self.final_answer = "h ∘ g ∘ f: A → D"
            steps.append("Шаг 1: Определяем область и кообласть каждого морфизма.")
            steps.append("f: A → B, g: B → C, h: C → D")
            steps.append("Шаг 2: Применяем морфизмы последовательно, начиная справа.")
            steps.append("Композиция (h ∘ g ∘ f) отображает область первого морфизма (f) в кообласть последнего (h).")
            steps.append(f"Результат: {self.final_answer}")

        elif self.task_type == "commutative_diagram":
            if self.is_commutative:
                self.final_answer = "Да"
                reason = "Диаграмма коммутирует, так как h ∘ f = k ∘ g."
            else:
                self.final_answer = "Нет"
                reason = "Диаграмма не коммутирует, так как h ∘ f ≠ k ∘ g."
            steps.append("Проверяем равенство двух путей из A в D.")
            steps.append(f"Путь 1: h ∘ f. Путь 2: k ∘ g.")
            steps.append(reason)
        
        self.solution_steps.extend(steps)

    @classmethod
    def generate_random_task(cls, task_type=None,
                           language: str = "ru", detail_level: int = 3):
        task_type = task_type or random.choice(["morphism_composition", "commutative_diagram"])
        # category_type is currently unused, so not passing it here.
        return cls(task_type=task_type, language=language, 
                 detail_level=detail_level)