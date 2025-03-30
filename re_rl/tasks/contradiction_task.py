import random
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class ContradictionTask(BaseTask):
    """
    Задача на выявление ложного утверждения.
    
    Генерируется длинный список утверждений (не менее num_statements),
    взятых из базы истинных фактов (ключ "true"). Затем одно случайное утверждение заменяется
    на ложное, взятое из базы ложных фактов (ключ "false").
    
    Все текстовые строки получаются из шаблонов в PROMPT_TEMPLATES.
    """
    def __init__(
        self,
        language: str = "en",
        num_statements: int = 25
    ):
        """
        :param language: 'ru' или 'en'
        :param num_statements: сколько утверждений использовать (по умолчанию 25)
        """
        self.language = language.lower()
        self.num_statements = num_statements
        self.statements = []
        self.false_statement_index = None
        description = self._create_problem_description()
        super().__init__(description)

    def _create_problem_description(self):
        facts_true = PROMPT_TEMPLATES["contradiction_facts"].get(self.language, {}).get("true", [])
        facts_false = PROMPT_TEMPLATES["contradiction_facts"].get(self.language, {}).get("false", [])
        
        # Проверяем, что у нас достаточно фактов
        if len(facts_true) < self.num_statements or len(facts_false) < self.num_statements:
            raise ValueError(f"База фактов должна содержать не менее чем {self.num_statements} истинных и {self.num_statements} ложных утверждений.")
        
        # Выбираем случайный набор из num_statements истинных утверждений без повторений
        selected = random.sample(facts_true, self.num_statements)
        
        # Выбираем случайный индекс для замены
        index = random.randint(0, self.num_statements - 1)
        self.false_statement_index = index
        
        # Выбираем ложное утверждение из базы (также случайное)
        false_statement = random.choice(facts_false)
        selected[index] = false_statement
        self.statements = selected
        
        # Формируем расширенный промпт с инструкциями
        problem_template = PROMPT_TEMPLATES["contradiction"]["problem"].get(self.language, PROMPT_TEMPLATES["contradiction"]["problem"]["en"])
        instructions = PROMPT_TEMPLATES["contradiction"]["instructions"].get(self.language, PROMPT_TEMPLATES["contradiction"]["instructions"]["en"])
        
        # Добавляем пример рассуждений
        example = PROMPT_TEMPLATES["contradiction"]["example"].get(self.language, PROMPT_TEMPLATES["contradiction"]["example"]["en"])
        
        # Формируем описание задачи
        statements_text = '\n'.join(f'- {s}' for s in selected)
        description = f"""{instructions}

{example}

{problem_template.format(statements=statements_text)}"""
        return description

    def solve(self):
        steps = []
        
        # Базовый шаг с общей стратегией
        base_step = PROMPT_TEMPLATES["contradiction"]["step1"].get(self.language, PROMPT_TEMPLATES["contradiction"]["step1"]["en"])
        steps.append(base_step)
        
        # Анализ по группам утверждений
        if self.num_statements > 10:
            group_size = 5
            for i in range(0, self.num_statements, group_size):
                group = self.statements[i:i + group_size]
                group_text = '\n'.join(f'- {s}' for s in group)
                if self.language == "ru":
                    group_step = f"""Анализ группы утверждений {i+1}-{min(i+group_size, self.num_statements)}:

{group_text}"""
                else:
                    group_step = f"""Analysis of statements {i+1}-{min(i+group_size, self.num_statements)}:

{group_text}"""
                steps.append(group_step)
        
        # Дополнительный анализ для больших задач
        if self.num_statements > 120:
            if self.language == "ru":
                extra = f"Дополнительный анализ: среди {self.num_statements} утверждений наиболее сомнительным выглядит утверждение №{self.false_statement_index + 1}."
            else:
                extra = f"Additional analysis: among {self.num_statements} statements, the most questionable is number {self.false_statement_index + 1}."
            steps.append(extra)
        
        # Финальный шаг с объяснением
        final_template = PROMPT_TEMPLATES["contradiction"]["final_answer"].get(self.language, PROMPT_TEMPLATES["contradiction"]["final_answer"]["en"])
        explanation = PROMPT_TEMPLATES["contradiction"]["explanation"].get(self.language, PROMPT_TEMPLATES["contradiction"]["explanation"]["en"])
        
        self.solution_steps = steps
        self.final_answer = f"""{final_template.format(false_statement=self.statements[self.false_statement_index])}

{explanation}"""

    def get_result(self) -> dict:
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),  # Здесь prompt совпадает с description
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
