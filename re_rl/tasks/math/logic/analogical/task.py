from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/analogical_task.py

from re_rl.tasks.base_task import BaseTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class AnalogicalTask(BaseTask):
    """
    Задача на аналогическое решение.
    Все текстовые строки извлекаются из шаблонов.
    detail_level определяет число шагов рассуждений.
    """
    def __init__(self, description: str, language: str = "en", detail_level: int = 3, output_format: OutputFormat = "text", reasoning_mode: bool = False):
        self.language = language.lower()
        self.detail_level = detail_level
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        problem_template = PROMPT_TEMPLATES["analogical"]["problem"].get(self.language, PROMPT_TEMPLATES["analogical"]["problem"]["en"])
        full_description = problem_template.format(description=description)
        # Сохраняем описание напрямую
        self.description = full_description
        self.solution_steps = []
        self.final_answer = None
        self.reasoning_mode = reasoning_mode

    def generate_prompt(self) -> str:
        # Возвращаем описание как есть, без оборачивания
        return self.description

    def solve(self):
        lang = self.language
        steps_full = []
        steps_full = [
            PROMPT_TEMPLATES["analogical"]["step1"][texts.t('s0', lang)],
            PROMPT_TEMPLATES["analogical"]["step2"][texts.t('s1', lang)],
            PROMPT_TEMPLATES["analogical"]["step3"][texts.t('s2', lang)],
            PROMPT_TEMPLATES["analogical"]["step4"][texts.t('s3', lang)]
        ]
        self.solution_steps = steps_full
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
