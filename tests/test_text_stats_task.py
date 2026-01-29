# tests/test_text_stats_generation.py

import unittest
from re_rl.tasks.math.logic.text_stats_task import TextStatsTask

class TestTextStatsGeneration(unittest.TestCase):

    def test_words_mode_ru(self):
        task = TextStatsTask(language="ru", text_gen_mode="words", detail_level=2)
        result = task.get_result()
        # Проверяем, что сгенерированный текст НЕ состоит из сплошных букв (скорее из слов, разделённых пробелами)
        self.assertIn(" ", task.text, "Текст в режиме words обычно содержит пробелы между словами")
        self.assertTrue(len(result["solution_steps"]) > 0)
        self.assertIn("Итоговый ответ:", result["final_answer"])

    def test_letters_mode_en(self):
        task = TextStatsTask(language="en", text_gen_mode="letters", detail_level=3)
        result = task.get_result()
        # В режиме letters текст - одна непрерывная строка случайных букв/цифр
        self.assertNotIn(" ", task.text, "В letters mode обычно нет пробелов (или крайне мало)")
        self.assertIn("Final answer:", result["final_answer"])

    def test_mixed_mode(self):
        task = TextStatsTask(language="en", text_gen_mode="mixed", mix_ratio=0.3, detail_level=1)
        result = task.get_result()
        # Ожидаем, что часть токенов будут «словами» из vocab, часть - рандомными буквами
        # Простейшая проверка: текст содержит хотя бы один пробел (значит есть несколько chunk'ов)
        self.assertIn(" ", task.text)

    def test_substring_count_overlapping(self):
        # вручную зададим text и substring, чтобы проверить количество пересечений
        text = "aaaaa"
        substring = "aa"
        task = TextStatsTask(
            language="ru",
            text=text,
            substring=substring,
            allow_overlapping=True
        )
        result = task.get_result()
        # "aaaaa" и "aa" => индексы: 0..1, 1..2, 2..3, 3..4 => 4 вхождения
        self.assertIn("4", result["final_answer"])

    def test_substring_count_no_overlap(self):
        text = "aaaaa"
        substring = "aa"
        task = TextStatsTask(
            language="ru",
            text=text,
            substring=substring,
            allow_overlapping=False
        )
        result = task.get_result()
        # без пересечений: "aaaaa" -> "aa" + "aa" + "a" => 2 вхождения
        self.assertIn("2", result["final_answer"])


if __name__ == "__main__":
    unittest.main()
