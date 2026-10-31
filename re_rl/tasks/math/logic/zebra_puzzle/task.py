from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/math/logic/zebra_puzzle_task.py

import random
from typing import Dict, Any, ClassVar, List, Tuple, Optional
from re_rl.tasks.math.logic.deduction_search import zebra_model,query_answer,zebra_answer,zebra_valid
import json

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


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

    TASK_TYPE = "zebra_puzzle"

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
            num_houses = 5 if num_houses is None else num_houses
            num_categories = 5 if num_categories is None else num_categories
            num_clues = 10 if num_clues is None else num_clues
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.difficulty = difficulty
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        
        if type(num_houses) is not int or not 2 <= num_houses <= 5:
            raise ValueError('invalid_num_houses')
        if type(num_categories) is not int or not 2 <= num_categories <= 5:
            raise ValueError('invalid_num_categories')
        if type(num_clues) is not int or not 0 <= num_clues <= 100:
            raise ValueError('invalid_num_clues')
        self.num_houses = num_houses
        self.num_categories = num_categories
        self.num_clues = num_clues
        
        # Выбираем категории
        self.categories = self.CATEGORY_NAMES[:self.num_categories]
        
        self.category_values = {cat:self._get_category_values(cat) for cat in self.categories}

        # Генерируем решение
        self.solution = self._generate_solution()
        
        # Генерируем подсказки
        self.clues = self._generate_clues()
        
        # Генерируем вопрос
        self.question, self.answer = self._generate_question()
        self._ensure_answer_unique()
        
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
                cat1,attr1,cat2,attr2 = cat2,attr2,cat1,attr1
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
            self.query = ("owner","pet",pet,"nationality")
            house_idx = self.solution["pet"].index(pet) if pet in self.solution["pet"] else 0
            if "nationality" in self.categories:
                answer = self.solution["nationality"][house_idx]
            else:
                answer = texts.t('house_answer',self.language,position=house_idx+1)
            question = templates[self.language][0].format(pet=pet)
        elif "drink" in self.categories:
            drink = random.choice(self._get_category_values("drink"))
            self.query = ("owner","drink",drink,"nationality")
            house_idx = self.solution["drink"].index(drink) if drink in self.solution["drink"] else 0
            if "nationality" in self.categories:
                answer = self.solution["nationality"][house_idx]
            else:
                answer = texts.t('house_answer',self.language,position=house_idx+1)
            question = templates[self.language][1].format(drink=drink)
        else:
            cat = random.choice(self.categories)
            val = random.choice(self.solution[cat])
            house_idx = self.solution[cat].index(val)
            self.query = ("position",cat,val)
            answer = texts.t('house_answer',self.language,position=house_idx+1)
            question = get_template(
                PROMPT_TEMPLATES["inline"],
                texts.t('s6', self.language),
                self.language,
                augment=False,
                value=val,
            )
        
        return question, answer

    def _create_problem_text(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES["zebra_puzzle"]
        
        # Форматируем категории
        categories_text = "; ".join(texts.t("category_"+cat,self.language)+": "+", ".join(self.category_values[cat]) for cat in self.categories)
        
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
        header = [texts.t("house_header",self.language)] + [texts.t("category_"+cat,self.language) for cat in self.categories]
        lines.append(" | ".join(header))
        lines.append("-" * len(lines[0]))
        
        for i in range(self.num_houses):
            row = [str(i + 1)]
            for cat in self.categories:
                row.append(self.solution[cat][i])
            lines.append(" | ".join(row))
        
        return "\n".join(lines)

    def _ensure_answer_unique(self):
        expected = query_answer(self.solution,self.query)
        for _ in range(self.num_houses*self.num_categories+1):
            alternative = zebra_model(self.num_houses,self.category_values,self.clues,forbidden=(self.query,expected))
            if alternative is None:return
            differing = [(cat,value) for cat in self.categories for value in self.category_values[cat]
                         if self.solution[cat].index(value) != alternative[cat].index(value)]
            if not differing:raise ValueError('generation_failed')
            cat,value = random.choice(differing)
            position = self.solution[cat].index(value)
            text = PROMPT_TEMPLATES['zebra_puzzle']['clue_templates']['position'][self.language].format(attr=value,pos=position+1)
            self.clues.append(dict(type='position',data=(cat,value,position),text=text))
        raise ValueError('generation_failed')

    def _public_fingerprint(self):
        return json.dumps([self.num_houses,self.category_values,[(c['type'],c['data']) for c in self.clues],self.query],sort_keys=True,ensure_ascii=False)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = []
        self.final_answer = PROMPT_TEMPLATES['zebra_puzzle']['final_answer'][self.language].format(
            answer=self.answer,table=self._format_solution_table())

    def verify(self,prediction):
        from re_rl.tasks.math.logic._logic_utils import clean
        from re_rl.tasks.math.planning.plan_verification import match_template
        certificate = getattr(self,'_answer_certificate',None)
        if certificate is None or certificate[0] != self._public_fingerprint():
            try:self.solve()
            except (ValueError,KeyError):return 0.0
        text = clean(prediction)
        expected = self._answer_certificate[1]
        aliases = [str(expected)] if self.query[0] == 'owner' else [str(expected+1)]+[
            texts.t('house_answer',lang,position=expected+1) for lang in ('ru','en')]
        if text in aliases:return 1.0
        for lang in ('ru','en'):
            fields = match_template(PROMPT_TEMPLATES['zebra_puzzle']['final_answer'][lang],text)
            if fields is None or fields['answer'] not in aliases:continue
            lines = fields['table'].splitlines()
            header = [texts.t('house_header',lang)]+[texts.t('category_'+cat,lang) for cat in self.categories]
            if len(lines) != self.num_houses+2 or [s.strip() for s in lines[0].split('|')] != header:continue
            if not lines[1] or set(lines[1]) != {'-'}:continue
            model = {cat:[] for cat in self.categories}
            for index,line in enumerate(lines[2:],1):
                row = [v.strip() for v in line.split('|')]
                if len(row) != self.num_categories+1 or row[0] != str(index):break
                for cat,value in zip(self.categories,row[1:]):model[cat].append(value)
            else:
                if zebra_valid(self.num_houses,self.category_values,self.clues,model) and query_answer(model,self.query) == expected:return 1.0
        return 0.0

    def get_task_type(self):
        return "zebra_puzzle"
