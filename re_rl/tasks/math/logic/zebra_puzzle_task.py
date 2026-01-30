# re_rl/tasks/math/logic/zebra_puzzle_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple, Optional
from z3 import Solver, Int, And, Distinct, sat, Or, Abs

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES


class ZebraPuzzleTask(BaseMathTask):
    """
    Генерирует и решает логические головоломки типа 'Загадка Эйнштейна'.
    
    Параметры сложности:
      - difficulty 1-2: 3 дома, 2 категории, 4-5 подсказок
      - difficulty 3-4: 4 дома, 3 категории, 6-8 подсказок
      - difficulty 5-6: 4 дома, 4 категории, 8-10 подсказок
      - difficulty 7-8: 5 домов, 4 категории, 10-12 подсказок
      - difficulty 9-10: 5 домов, 5 категорий, 12-15 подсказок
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_houses": 3, "num_categories": 2, "num_clues": 4},
        2: {"num_houses": 3, "num_categories": 2, "num_clues": 5},
        3: {"num_houses": 4, "num_categories": 3, "num_clues": 6},
        4: {"num_houses": 4, "num_categories": 3, "num_clues": 8},
        5: {"num_houses": 4, "num_categories": 4, "num_clues": 8},
        6: {"num_houses": 4, "num_categories": 4, "num_clues": 10},
        7: {"num_houses": 5, "num_categories": 4, "num_clues": 10},
        8: {"num_houses": 5, "num_categories": 4, "num_clues": 12},
        9: {"num_houses": 5, "num_categories": 5, "num_clues": 12},
        10: {"num_houses": 5, "num_categories": 5, "num_clues": 15},
    }

    CATEGORY_NAMES = ["nationality", "color", "drink", "pet", "cigarette"]

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        num_houses: int = None,
        num_categories: int = None,
        num_clues: int = None,
        difficulty: int = None,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: количество шагов chain-of-thought
        :param num_houses: количество домов (3-5)
        :param num_categories: количество категорий (2-5)
        :param num_clues: количество подсказок
        :param difficulty: уровень сложности (1-10)
        :param output_format: формат вывода ('text' или 'latex')
        """
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if num_houses is None:
                num_houses = preset.get("num_houses", 5)
            if num_categories is None:
                num_categories = preset.get("num_categories", 5)
            if num_clues is None:
                num_clues = preset.get("num_clues", 10)
        else:
            num_houses = num_houses or 5
            num_categories = num_categories or 5
            num_clues = num_clues or 10
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        self.num_houses = num_houses
        self.num_categories = min(num_categories, len(self.CATEGORY_NAMES))
        self.num_clues = num_clues
        
        # Выбираем категории
        self.categories = self.CATEGORY_NAMES[:self.num_categories]
        
        # Генерируем решение
        self.solution = self._generate_solution()
        
        # Генерируем подсказки
        self.clues = self._generate_clues()
        
        # Генерируем вопрос
        self.question, self.answer = self._generate_question()
        
        # Формируем текст задачи
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text, language=self.language, detail_level=detail_level, output_format=output_format)
        self.reasoning_mode = reasoning_mode

    def _get_category_values(self, category: str) -> List[str]:
        """Получает значения для категории на нужном языке."""
        templates = PROMPT_TEMPLATES["zebra_puzzle"]["categories_pool"]
        if category in templates:
            values = templates[category][self.language][:self.num_houses]
        else:
            # Генерируем числовые значения как fallback
            values = [str(i) for i in range(1, self.num_houses + 1)]
        return values

    def _generate_solution(self) -> Dict[str, List[str]]:
        """Генерирует случайное решение головоломки."""
        solution = {}
        for category in self.categories:
            values = self._get_category_values(category)
            random.shuffle(values)
            solution[category] = values[:self.num_houses]
        return solution

    def _generate_clues(self) -> List[Dict[str, Any]]:
        """Генерирует подсказки на основе решения."""
        clues = []
        templates = PROMPT_TEMPLATES["zebra_puzzle"]["clue_templates"]
        
        clue_types = ["same_house", "neighbor", "left_of", "position", "middle", "first"]
        
        attempts = 0
        max_attempts = self.num_clues * 10
        
        while len(clues) < self.num_clues and attempts < max_attempts:
            attempts += 1
            clue_type = random.choice(clue_types)
            
            try:
                clue = self._create_clue(clue_type, templates)
                if clue and clue not in clues:
                    clues.append(clue)
            except (IndexError, KeyError):
                continue
        
        return clues

    def _create_clue(self, clue_type: str, templates: Dict) -> Optional[Dict[str, Any]]:
        """Создаёт одну подсказку заданного типа."""
        if clue_type == "same_house":
            # Две характеристики в одном доме
            cat1, cat2 = random.sample(self.categories, 2)
            house = random.randint(0, self.num_houses - 1)
            attr1 = self.solution[cat1][house]
            attr2 = self.solution[cat2][house]
            text = templates["same_house"][self.language].format(attr1=attr1, attr2=attr2)
            return {"type": clue_type, "text": text, "data": (cat1, attr1, cat2, attr2)}
        
        elif clue_type == "neighbor":
            # Соседние дома
            if self.num_houses < 2:
                return None
            house1 = random.randint(0, self.num_houses - 2)
            house2 = house1 + 1
            cat1 = random.choice(self.categories)
            cat2 = random.choice(self.categories)
            attr1 = self.solution[cat1][house1]
            attr2 = self.solution[cat2][house2]
            if random.random() < 0.5:
                attr1, attr2 = attr2, attr1
            text = templates["neighbor"][self.language].format(attr1=attr1, attr2=attr2)
            return {"type": clue_type, "text": text, "data": (cat1, attr1, cat2, attr2)}
        
        elif clue_type == "left_of":
            # Один слева от другого
            if self.num_houses < 2:
                return None
            house1 = random.randint(0, self.num_houses - 2)
            house2 = random.randint(house1 + 1, self.num_houses - 1)
            cat1 = random.choice(self.categories)
            cat2 = random.choice(self.categories)
            attr1 = self.solution[cat1][house1]
            attr2 = self.solution[cat2][house2]
            text = templates["left_of"][self.language].format(attr1=attr1, attr2=attr2)
            return {"type": clue_type, "text": text, "data": (cat1, attr1, cat2, attr2)}
        
        elif clue_type == "position":
            # Конкретная позиция
            house = random.randint(0, self.num_houses - 1)
            cat = random.choice(self.categories)
            attr = self.solution[cat][house]
            text = templates["position"][self.language].format(attr=attr, pos=house + 1)
            return {"type": clue_type, "text": text, "data": (cat, attr, house)}
        
        elif clue_type == "middle":
            # Центральный дом
            if self.num_houses % 2 == 0:
                return None
            middle = self.num_houses // 2
            cat = random.choice(self.categories)
            attr = self.solution[cat][middle]
            text = templates["middle"][self.language].format(attr=attr)
            return {"type": clue_type, "text": text, "data": (cat, attr, middle)}
        
        elif clue_type == "first":
            # Первый дом
            cat = random.choice(self.categories)
            attr = self.solution[cat][0]
            text = templates["first"][self.language].format(attr=attr)
            return {"type": clue_type, "text": text, "data": (cat, attr, 0)}
        
        return None

    def _generate_question(self) -> Tuple[str, str]:
        """Генерирует вопрос и ответ."""
        templates = PROMPT_TEMPLATES["zebra_puzzle"]["questions"]
        
        # Выбираем случайную категорию для вопроса
        if "pet" in self.categories:
            pet = random.choice(self._get_category_values("pet"))
            house_idx = self.solution["pet"].index(pet) if pet in self.solution["pet"] else 0
            if "nationality" in self.categories:
                answer = self.solution["nationality"][house_idx]
            else:
                answer = f"house {house_idx + 1}"
            question = templates[self.language][0].format(pet=pet)
        elif "drink" in self.categories:
            drink = random.choice(self._get_category_values("drink"))
            house_idx = self.solution["drink"].index(drink) if drink in self.solution["drink"] else 0
            if "nationality" in self.categories:
                answer = self.solution["nationality"][house_idx]
            else:
                answer = f"house {house_idx + 1}"
            question = templates[self.language][1].format(drink=drink)
        else:
            cat = random.choice(self.categories)
            val = random.choice(self.solution[cat])
            house_idx = self.solution[cat].index(val)
            answer = f"house {house_idx + 1}"
            question = f"В каком доме живёт человек с {val}?" if self.language == "ru" else f"Which house has {val}?"
        
        return question, answer

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES["zebra_puzzle"]
        
        # Форматируем категории
        categories_text = ", ".join(self.categories)
        
        # Форматируем подсказки
        clues_text = "\n".join([f"{i + 1}. {clue['text']}" for i, clue in enumerate(self.clues)])
        
        problem_text = templates["instructions"][self.language] + "\n\n"
        problem_text += templates["problem"][self.language].format(
            n=self.num_houses,
            categories=categories_text,
            clues=clues_text,
            question=self.question
        )
        
        return problem_text

    def _format_solution_table(self) -> str:
        """Форматирует решение в виде таблицы."""
        lines = []
        header = ["House"] + self.categories
        lines.append(" | ".join(header))
        lines.append("-" * len(lines[0]))
        
        for i in range(self.num_houses):
            row = [str(i + 1)]
            for cat in self.categories:
                row.append(self.solution[cat][i])
            lines.append(" | ".join(row))
        
        return "\n".join(lines)

    def solve(self):
        """Генерирует пошаговое решение."""
        templates = PROMPT_TEMPLATES["zebra_puzzle"]
        steps = []
        
        # Генерируем шаги на основе подсказок
        for i, clue in enumerate(self.clues):
            deduction = self._describe_deduction(clue)
            step = templates["steps"]["from_clue"][self.language].format(
                n=i + 1, deduction=deduction
            )
            steps.append(step)
        
        # Добавляем шаги с методом исключения
        for _ in range(len(self.clues), len(self.clues) + 3):  # Добавляем несколько шагов исключения
            deduction = self._generate_elimination_step()
            step = templates["steps"]["elimination"][self.language].format(deduction=deduction)
            steps.append(step)
        
        self.solution_steps = steps
        self.final_answer = templates["final_answer"][self.language].format(
            answer=self.answer,
            table=self._format_solution_table()
        )

    def _describe_deduction(self, clue: Dict[str, Any]) -> str:
        """Описывает вывод из подсказки."""
        clue_type = clue["type"]
        data = clue["data"]
        
        if self.language == "ru":
            if clue_type == "same_house":
                return f"{data[1]} и {data[3]} находятся в одном доме"
            elif clue_type == "neighbor":
                return f"{data[1]} и {data[3]} — соседи"
            elif clue_type == "left_of":
                return f"{data[1]} левее {data[3]}"
            elif clue_type == "position":
                return f"{data[1]} в доме {data[2] + 1}"
            elif clue_type in ("middle", "first"):
                return f"{data[1]} в доме {data[2] + 1}"
        else:
            if clue_type == "same_house":
                return f"{data[1]} and {data[3]} are in the same house"
            elif clue_type == "neighbor":
                return f"{data[1]} and {data[3]} are neighbors"
            elif clue_type == "left_of":
                return f"{data[1]} is to the left of {data[3]}"
            elif clue_type == "position":
                return f"{data[1]} is in house {data[2] + 1}"
            elif clue_type in ("middle", "first"):
                return f"{data[1]} is in house {data[2] + 1}"
        
        return clue["text"]

    def _generate_elimination_step(self) -> str:
        """Генерирует шаг с методом исключения."""
        cat = random.choice(self.categories)
        house = random.randint(0, self.num_houses - 1)
        val = self.solution[cat][house]
        
        if self.language == "ru":
            return f"{val} может быть только в доме {house + 1}"
        else:
            return f"{val} can only be in house {house + 1}"

    def get_task_type(self):
        return "zebra_puzzle"
