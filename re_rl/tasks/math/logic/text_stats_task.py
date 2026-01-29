# re_rl/tasks/text_stats_task.py

import random
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class TextStatsTask(BaseMathTask):
    """
    Задача: подсчитать количество вхождений некоторой подстроки в случайном тексте.
    
    :param language: 'ru' или 'en'.
    :param detail_level: сколько шагов показывать в chain-of-thought.
    :param text: если None, генерируем случайный текст.
    :param substring: если None, выберем случайный фрагмент из text.
    :param allow_overlapping: учитывать ли пересечение вхождений.
    :param text_gen_mode: 'words' | 'letters' | 'mixed'
        - 'words': берем слова из PROMPT_TEMPLATES["text_stats"]["vocab"][lang]
        - 'letters': берем случайные символы из PROMPT_TEMPLATES["text_stats"]["alphabet"][lang]
        - 'mixed': часть слов, часть символов
    :param mix_ratio: (float) при text_gen_mode='mixed' указывает,
                      какую долю вставлять из слов (например, 0.5 => 50% слов, 50% случайных букв)
    """

    def __init__(self,
                 language: str = "ru",
                 detail_level: int = 3,
                 text: str = None,
                 substring: str = None,
                 allow_overlapping: bool = False,
                 text_gen_mode: str = "words",
                 mix_ratio: float = 0.5,
                 output_format: OutputFormat = "text"):
        self.language = language.lower()
        self.detail_level = detail_level
        self._output_format = output_format
        self.allow_overlapping = allow_overlapping
        self.text_gen_mode = text_gen_mode
        self.mix_ratio = mix_ratio
        
        if text is None:
            text = self._generate_random_text()
        self.text = text
        
        if substring is None:
            self.substring = self._choose_random_substring(self.text)
        else:
            self.substring = substring
        
        # Формируем описание задачи (problem)
        problem_templ = PROMPT_TEMPLATES["text_stats"]["problem"].get(
            self.language,
            PROMPT_TEMPLATES["text_stats"]["problem"]["en"]
        )
        desc = problem_templ.format(
            substring=self.substring,
            text=self.text
        )
        
        super().__init__(desc, language=language, detail_level=detail_level, output_format=output_format)

    def _generate_random_text(self) -> str:
        """Генерируем текст в зависимости от text_gen_mode."""
        # Достаём из prompts
        vocab_list = PROMPT_TEMPLATES["text_stats"]["vocab"].get(
            self.language,
            PROMPT_TEMPLATES["text_stats"]["vocab"]["en"]
        )
        alphabet_str = PROMPT_TEMPLATES["text_stats"]["alphabet"].get(
            self.language,
            PROMPT_TEMPLATES["text_stats"]["alphabet"]["en"]
        )

        length = random.randint(6, 15)  # количество «элементов» (слов или кусков)
        chunks = []

        if self.text_gen_mode == "words":
            # Генерируем только «слова» из vocab_list
            chunks = random.choices(vocab_list, k=length)
            return " ".join(chunks)

        elif self.text_gen_mode == "letters":
            # Генерируем одну строку полностью из случайных букв/цифр
            # (Можно разрезать на слова, но пусть будет как единый «текст».)
            total_chars = random.randint(15, 50)
            return "".join(random.choices(alphabet_str, k=total_chars))

        else:
            # mixed: часть слов, часть рандомных букв
            # mix_ratio отвечает за долю слов, всё остальное — буквы.
            # Например, если mix_ratio=0.7, ~70% chunks будут «словами».
            for _ in range(length):
                if random.random() < self.mix_ratio:
                    # слово
                    chunks.append(random.choice(vocab_list))
                else:
                    # случайная буквенная подстрока, длиной 2..6
                    sub_len = random.randint(2, 6)
                    rnd_sub = "".join(random.choices(alphabet_str, k=sub_len))
                    chunks.append(rnd_sub)
            # Склеим через пробел (или можно через рандомные пробелы и т.д.)
            return " ".join(chunks)

    def _choose_random_substring(self, text: str) -> str:
        """Выбираем случайный кусок из текста, размером 1..3 символа."""
        if not text:
            return "a"
        start_idx = random.randint(0, len(text) - 1)
        max_sub_len = min(3, len(text) - start_idx)
        sub_len = random.randint(1, max_sub_len)
        return text[start_idx : start_idx + sub_len]

    def solve(self):
        steps_templates = PROMPT_TEMPLATES["text_stats"]["steps"].get(
            self.language,
            PROMPT_TEMPLATES["text_stats"]["steps"]["en"]
        )
        steps_count = min(self.detail_level, len(steps_templates))
        self.solution_steps = []

        for i in range(steps_count):
            step_str = steps_templates[i].format(
                substring=self.substring,
                allow_overlapping=self.allow_overlapping
            )
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
        if not sub:
            return 0
        count = 0
        start = 0
        while True:
            idx = text.find(sub, start)
            if idx == -1:
                break
            count += 1
            start = idx + 1
        return count

    def get_task_type(self) -> str:
        return "text_stats"
