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
    def __init__(self, language: str = "en", num_statements: int = 100):
        self.language = language.lower()
        self.num_statements = num_statements
        self.statements = []
        self.false_statement_index = None
        description = self._create_problem_description()
        super().__init__(description)

    def _create_problem_description(self):
        facts_true = PROMPT_TEMPLATES["contradiction_facts"].get(self.language, {}).get("true", [])
        facts_false = PROMPT_TEMPLATES["contradiction_facts"].get(self.language, {}).get("false", [])
        # Если базы меньше 100, можно расширить их (для простоты здесь предполагаем, что их ровно 100)
        if len(facts_true) < self.num_statements or len(facts_false) < self.num_statements:
            raise ValueError("База фактов должна содержать не менее чем 100 истинных и 100 ложных утверждений.")
        # Выбираем случайный набор из num_statements истинных утверждений без повторений
        selected = random.sample(facts_true, self.num_statements)
        # Выбираем случайный индекс для замены
        index = random.randint(0, self.num_statements - 1)
        self.false_statement_index = index
        # Выбираем ложное утверждение из базы (также случайное)
        false_statement = random.choice(facts_false)
        selected[index] = false_statement
        self.statements = selected
        problem_template = PROMPT_TEMPLATES["contradiction"]["problem"].get(self.language, PROMPT_TEMPLATES["contradiction"]["problem"]["en"])
        description = problem_template.format(statements="\n".join(f"- {s}" for s in selected))
        return description

    def solve(self):
        steps = []
        base_step = PROMPT_TEMPLATES["contradiction"]["step1"].get(self.language, PROMPT_TEMPLATES["contradiction"]["step1"]["en"])
        steps.append(base_step)
        if self.num_statements > 120:
            if self.language == "ru":
                extra = f"Дополнительный анализ: среди {self.num_statements} утверждений наиболее сомнительным выглядит утверждение №{self.false_statement_index + 1}."
            else:
                extra = f"Additional analysis: among {self.num_statements} statements, the most questionable is number {self.false_statement_index + 1}."
            steps.append(extra)
        final_template = PROMPT_TEMPLATES["contradiction"]["final_answer"].get(self.language, PROMPT_TEMPLATES["contradiction"]["final_answer"]["en"])
        self.solution_steps = steps
        self.final_answer = final_template.format(false_statement=self.statements[self.false_statement_index])

    def get_result(self) -> dict:
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),  # Здесь prompt совпадает с description
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
