# re_rl/tasks/text_stats_task.py
import random
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class TextStatsTask(BaseTask):
    """
    Задача: подсчитать количество вхождений некоторой подстроки в случайном тексте.
    
    Можно расширять и усложнять: например, считать отдельные буквы или пересекающиеся подстроки, 
    генерировать случайные тексты и т.д.
    """
    def __init__(self, 
                 language: str = "ru", 
                 detail_level: int = 3,
                 text: str = None,
                 substring: str = None,
                 allow_overlapping: bool = False):
        """
        :param language: 'ru' или 'en'.
        :param detail_level: сколько шагов показывать в chain-of-thought.
        :param text: если None, сгенерируем случайный текст.
        :param substring: если None, выберем случайную подстроку (1..3 символа).
        :param allow_overlapping: учитывать ли пересечение вхождений, 
               напр. в строке 'aaaa' подстрока 'aa' встречается 3 раза, если считать пересечения.
        """
        self.language = language.lower()
        self.detail_level = detail_level
        self.allow_overlapping = allow_overlapping
        
        # Если текст не задан — генерируем простой случайный текст
        if text is None:
            text = self._generate_random_text()
        self.text = text
        
        # Если подстрока не задана — выберем случайно 1..3 символа из текста или алфавита
        if substring is None:
            substring = self._choose_random_substring(text)
        self.substring = substring
        
        # Формируем описание задачи (problem)
        problem_templ = PROMPT_TEMPLATES["text_stats"]["problem"].get(
            self.language, 
            PROMPT_TEMPLATES["text_stats"]["problem"]["en"]
        )
        description = problem_templ.format(
            substring=self.substring,
            text=self.text
        )
        
        super().__init__(description=description)

    def _generate_random_text(self) -> str:
        # Можно сделать более сложную генерацию. Для примера — 
        # возьмём набор букв, слов или коротких фраз.
        words = [
            "стул", "стол", "ресторан", "робот", "радар", 
            "рано", "ар", "aaa", "bb", "zzz", "привет", "сфера"
        ]
        # Сформируем случайную строку длиной 5..15 слов
        length = random.randint(5, 15)
        chosen = random.choices(words, k=length)
        text = " ".join(chosen)
        return text

    def _choose_random_substring(self, text: str) -> str:
        # Либо берём кусок из самого текста, либо рандомно
        if len(text) > 0:
            # Возьмём 1..3 символа в случайном месте
            start_idx = random.randint(0, max(0, len(text)-1))
            max_sub_len = min(3, len(text) - start_idx)
            sub_len = random.randint(1, max_sub_len)
            return text[start_idx:start_idx+sub_len]
        else:
            return "a"

    def solve(self):
        """
        Считаем количество вхождений подстроки. 
        Формируем фейковую цепочку рассуждений (solution_steps).
        """
        st_steps = PROMPT_TEMPLATES["text_stats"]["steps"].get(
            self.language, 
            PROMPT_TEMPLATES["text_stats"]["steps"]["en"]
        )
        # detail_level = сколько шагов хотим реально вывести
        steps_count = min(self.detail_level, len(st_steps))
        # Выбираем steps_count шагов
        self.solution_steps = []
        for i in range(steps_count):
            step_str = st_steps[i].format(substring=self.substring)
            self.solution_steps.append(step_str)
        
        # Подсчитаем вхождения
        if self.allow_overlapping:
            count_val = self._count_overlapping(self.text, self.substring)
        else:
            count_val = self.text.count(self.substring)
        
        final_templ = PROMPT_TEMPLATES["text_stats"]["final_answer"].get(
            self.language,
            PROMPT_TEMPLATES["text_stats"]["final_answer"]["en"]
        )
        self.final_answer = final_templ.format(
            substring=self.substring,
            count_value=count_val
        )

    def _count_overlapping(self, text: str, sub: str) -> int:
        """
        Подсчитывает вхождения подстроки (с учётом пересечений).
        Пример: 'aaaa'.count('aa') = 2, а с пересечением будет 3 ('aa'aa, a'aa'a, aa'aa').
        """
        if not sub:
            return 0
        count = 0
        start = 0
        while True:
            idx = text.find(sub, start)
            if idx == -1:
                break
            count += 1
            start = idx + 1  # сдвигаемся всего на 1
        return count

    def get_task_type(self):
        return "text_stats"
