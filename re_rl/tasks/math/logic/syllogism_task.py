"""SyllogismTask — проверка валидности категорического силлогизма.

Две посылки и заключение над тремя терминами (S, M, P). Валидность
определяется семантически: перебором всех вариантов занятости 8 областей
диаграммы Венна (булева интерпретация: All/No — универсальные, Some — с
экзистенциальным требованием).
"""

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_TERMS_RU = ["кошки", "млекопитающие", "хищники", "птицы", "рыбы", "растения",
             "философы", "смертные", "греки", "поэты", "учёные", "музыканты"]
_TERMS_EN = ["cats", "mammals", "predators", "birds", "fish", "plants",
             "philosophers", "mortals", "Greeks", "poets", "scientists", "musicians"]

# Квантификаторы: (ключ, шаблон ru, шаблон en)
_QUANT = {
    "all": ("Все {x} суть {y}.", "All {x} are {y}."),
    "no": ("Ни один {x} не есть {y}.", "No {x} are {y}."),
    "some": ("Некоторые {x} суть {y}.", "Some {x} are {y}."),
    "some_not": ("Некоторые {x} не суть {y}.", "Some {x} are not {y}."),
}


class SyllogismTask(BaseMathTask):
    TASK_TYPE = "syllogism"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        self.augment = augment
        self.difficulty = difficulty
        terms = (_TERMS_RU if language == "ru" else _TERMS_EN)
        self.S, self.M, self.P = random.sample(terms, 3)
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        # Индексы терминов в кортеже занятости региона: (S, M, P).
        idx = {"S": 0, "M": 1, "P": 2}
        # Посылки классической структуры: (M,P), (S,M); заключение (S,P).
        self.premise1 = (random.choice(list(_QUANT)), "M", "P")
        self.premise2 = (random.choice(list(_QUANT)), "S", "M")
        self.conclusion = (random.choice(list(_QUANT)), "S", "P")
        self._idx = idx
        self._valid = self._check_validity()

    def _stmt_holds(self, stmt, occupied) -> bool:
        """occupied — множество занятых регионов (кортежей 0/1 по (S,M,P))."""
        q, xk, yk = stmt
        xi, yi = self._idx[xk], self._idx[yk]
        if q == "all":  # нет региона X∧¬Y
            return not any(r[xi] == 1 and r[yi] == 0 for r in occupied)
        if q == "no":  # нет региона X∧Y
            return not any(r[xi] == 1 and r[yi] == 1 for r in occupied)
        if q == "some":  # есть регион X∧Y
            return any(r[xi] == 1 and r[yi] == 1 for r in occupied)
        return any(r[xi] == 1 and r[yi] == 0 for r in occupied)  # some_not

    def _check_validity(self) -> bool:
        regions = list(product([0, 1], repeat=3))  # 8 регионов
        for mask in product([0, 1], repeat=8):
            occupied = [regions[i] for i in range(8) if mask[i]]
            if self._stmt_holds(self.premise1, occupied) and self._stmt_holds(self.premise2, occupied):
                if not self._stmt_holds(self.conclusion, occupied):
                    return False  # контрмодель найдена
        return True

    def _fmt(self, stmt, ru: bool) -> str:
        q, xk, yk = stmt
        names = {"S": self.S, "M": self.M, "P": self.P}
        tmpl = _QUANT[q][0 if ru else 1]
        return tmpl.format(x=names[xk], y=names[yk])

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        head = ("Даны две посылки и заключение:\n" if ru else "Given two premises and a conclusion:\n")
        body = (f"1) {self._fmt(self.premise1, ru)}\n"
                f"2) {self._fmt(self.premise2, ru)}\n"
                f"{'Заключение' if ru else 'Conclusion'}: {self._fmt(self.conclusion, ru)}\n")
        tail = ("Следует ли заключение из посылок логически? Ответьте «верный» или «неверный»."
                if ru else
                "Does the conclusion logically follow from the premises? Answer 'valid' or 'invalid'.")
        return head + body + tail

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Строим диаграмму Венна для трёх терминов и проверяем, есть ли модель, "
             "где посылки истинны, а заключение ложно." if ru else
             "Build a Venn diagram for the three terms and check whether some model makes "
             "the premises true but the conclusion false."),
            ((("Контрмодель отсутствует — вывод корректен." if self._valid else
               "Существует контрмодель — вывод некорректен.")) if ru else
             (("No countermodel exists — the argument is valid." if self._valid else
               "A countermodel exists — the argument is invalid."))),
        ]
        if ru:
            self.final_answer = "верный" if self._valid else "неверный"
        else:
            self.final_answer = "valid" if self._valid else "invalid"

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        valid_syn = ["верный", "валиден", "valid", "корректный", "истинный"]
        invalid_syn = ["неверный", "невалиден", "invalid", "некорректный", "ложный"]
        found_valid = U.verify_label(prediction, valid_syn) == 1.0
        found_invalid = U.verify_label(prediction, invalid_syn) == 1.0
        if found_valid == found_invalid:  # оба или ни одного — неоднозначно
            return 0.0
        predicted_valid = found_valid
        return 1.0 if predicted_valid == self._valid else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
