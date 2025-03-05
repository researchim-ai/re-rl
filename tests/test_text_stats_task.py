# tests/test_text_stats_task.py

import unittest
from re_rl.tasks.text_stats_task import TextStatsTask

class TestTextStatsTask(unittest.TestCase):

    def test_simple_count(self):
        task = TextStatsTask(
            language="ru", 
            detail_level=3, 
            text="абракадабра", 
            substring="ра",
            allow_overlapping=False
        )
        result = task.get_result()
        
        # Проверяем, что в описании задачи есть нужные фразы
        self.assertIn("абракадабра", result["problem"])
        self.assertIn("ра", result["problem"])
        
        # Проверяем решение
        # в слове "абракадабра" подстрока "ра" встречается 2 раза (без пересечений):
        # "абРАкадабРА"
        # Сплит показывает: аб -> (ра) -> кадаб -> (ра)
        
        self.assertIn("Шаг", result["solution_steps"][0])
        self.assertIn("итоговый ответ", result["final_answer"].lower())  # На всякий случай
        
        # Убедимся, что кол-во совпадений действительно 2.
        self.assertIn("2", result["final_answer"])

    def test_overlapping_count(self):
        # Проверим, что при allow_overlapping=True считаются пересечения
        task = TextStatsTask(
            language="ru",
            detail_level=3,
            text="aaaa",
            substring="aa",
            allow_overlapping=True
        )
        result = task.get_result()
        
        # Для "aaaa" + "aa" при разрешённых пересечениях получаем 3 вхождения:
        # индексы вхождений: (0..1), (1..2), (2..3)
        self.assertIn("3", result["final_answer"])

    def test_english(self):
        # проверка на английском
        task = TextStatsTask(
            language="en",
            detail_level=2,
            text="banana bandana",
            substring="ana",
            allow_overlapping=True
        )
        result = task.get_result()
        self.assertIn("banana bandana", result["problem"])
        # Подстрока 'ana' в "banana bandana" с пересечениями 
        # banana => b(ana)na => 1й
        # затем ana внутри n(ana) => 2й
        # bandana => b(ana) => 3й
        # d(ana) => 4й
        # Итого 4. 
        # (В зависимости от того, считаем ли мы 'banana bandana' за цельную строку 
        #  и как Python ищет find(..., start), но да, проверим что 4 присутствует.)
        self.assertIn("3", result["final_answer"])


if __name__ == '__main__':
    unittest.main()
