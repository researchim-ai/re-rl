# re_rl/tasks/analogical_task.py

from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class AnalogicalTask(BaseTask):
    """
    Задача на аналогическое решение.
    Все текстовые строки извлекаются из шаблонов.
    detail_level определяет число шагов рассуждений.
    """
    def __init__(self, description: str, language: str = "en", detail_level: int = 3):
        self.language = language.lower()
        self.detail_level = detail_level
        problem_template = PROMPT_TEMPLATES["analogical"]["problem"].get(self.language, PROMPT_TEMPLATES["analogical"]["problem"]["en"])
        full_description = problem_template.format(description=description)
        # Сохраняем описание напрямую
        self.description = full_description
        self.solution_steps = []
        self.final_answer = None

    def generate_prompt(self) -> str:
        # Возвращаем описание как есть, без оборачивания
        return self.description

    def solve(self):
        lang = self.language
        steps_full = []
        if lang == "ru":
            steps_full = [
                PROMPT_TEMPLATES["analogical"]["step1"]["ru"],
                PROMPT_TEMPLATES["analogical"]["step2"]["ru"],
                PROMPT_TEMPLATES["analogical"]["step3"]["ru"],
                PROMPT_TEMPLATES["analogical"]["step4"]["ru"]
            ]
        else:
            steps_full = [
                PROMPT_TEMPLATES["analogical"]["step1"]["en"],
                PROMPT_TEMPLATES["analogical"]["step2"]["en"],
                PROMPT_TEMPLATES["analogical"]["step3"]["en"],
                PROMPT_TEMPLATES["analogical"]["step4"]["en"]
            ]
        num_steps = min(self.detail_level, len(steps_full))
        self.solution_steps = steps_full[:num_steps]
        final_template = PROMPT_TEMPLATES["analogical"]["final_answer"].get(lang, PROMPT_TEMPLATES["analogical"]["final_answer"]["en"])
        self.final_answer = final_template

    def get_result(self) -> dict:
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
