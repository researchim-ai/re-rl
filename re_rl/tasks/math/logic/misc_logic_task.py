"""Разные логические задачи: расшифровка шифра (Цезарь / подстановка), принцип
Дирихле, парадокс Монти Холла и отношения Аллена между интервалами."""

import random
import string
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _MiscBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


def _letters_only(s: str) -> str:
    return "".join(ch for ch in s.lower() if "a" <= ch <= "z")


class CipherDecodeTask(_MiscBase):
    TASK_TYPE = "cipher_decode"
    TASK_TYPES = ["caesar", "substitution"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 4, "alpha": 5}, 2: {"L": 5, "alpha": 6}, 3: {"L": 6, "alpha": 6},
        4: {"L": 7, "alpha": 7}, 5: {"L": 8, "alpha": 8}, 6: {"L": 9, "alpha": 8},
        7: {"L": 10, "alpha": 9}, 8: {"L": 11, "alpha": 10}, 9: {"L": 12, "alpha": 10},
        10: {"L": 14, "alpha": 12},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L = int(p["L"])
        self.alpha_size = int(p["alpha"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "caesar":
            self.shift = random.randint(1, 25)
            self.plain = "".join(random.choice(string.ascii_lowercase) for _ in range(self.L))
            self.cipher = "".join(chr((ord(ch) - 97 + self.shift) % 26 + 97) for ch in self.plain)
        else:
            self.alphabet = string.ascii_lowercase[:self.alpha_size]
            perm = list(self.alphabet)
            random.shuffle(perm)
            self.key = dict(zip(self.alphabet, perm))       # plain -> cipher
            self.inv = {c: p for p, c in self.key.items()}  # cipher -> plain
            self.plain = "".join(random.choice(self.alphabet) for _ in range(self.L))
            self.cipher = "".join(self.key[ch] for ch in self.plain)

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "caesar":
            return ((f"Шифр Цезаря со сдвигом {self.shift} (каждая буква сдвинута на {self.shift} позиций "
                     f"вперёд по латинскому алфавиту a–z с циклом). Зашифрованный текст: «{self.cipher}». "
                     f"Восстановите исходный текст.") if ru else
                    (f"Caesar cipher with shift {self.shift} (each letter shifted {self.shift} positions "
                     f"forward in the Latin alphabet a–z, wrapping around). Ciphertext: '{self.cipher}'. "
                     f"Recover the original text."))
        table = ", ".join(f"{p}→{self.key[p]}" for p in self.alphabet)
        return ((f"Шифр простой подстановки. Таблица (буква оригинала → буква шифра): {table}. "
                 f"Зашифрованный текст: «{self.cipher}». Восстановите исходный текст.") if ru else
                (f"Simple substitution cipher. Table (plain → cipher): {table}. "
                 f"Ciphertext: '{self.cipher}'. Recover the original text."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Применяем обратное преобразование к каждой букве шифра." if ru else
             "Apply the inverse transformation to each ciphertext letter."),
            (f"Исходный текст: {self.plain}." if ru else f"Original text: {self.plain}."),
        ]
        self.final_answer = self.plain

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return 1.0 if self.plain in _letters_only(prediction) else 0.0


class PigeonholeTask(_MiscBase):
    TASK_TYPE = "pigeonhole"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"cmax": 3, "kmax": 2}, 2: {"cmax": 4, "kmax": 2}, 3: {"cmax": 4, "kmax": 3},
        4: {"cmax": 5, "kmax": 3}, 5: {"cmax": 6, "kmax": 3}, 6: {"cmax": 6, "kmax": 4},
        7: {"cmax": 7, "kmax": 4}, 8: {"cmax": 8, "kmax": 5}, 9: {"cmax": 9, "kmax": 5},
        10: {"cmax": 10, "kmax": 6},
    }
    _ITEMS = {"ru": ["носков", "перчаток", "шаров", "карандашей", "конфет"],
              "en": ["socks", "gloves", "balls", "pencils", "candies"]}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.colors = random.randint(2, int(p["cmax"]))
        self.k = random.randint(2, int(p["kmax"]))
        self.augment = augment
        self.item = random.choice(self._ITEMS["ru" if language == "ru" else "en"])
        self.answer = self.colors * (self.k - 1) + 1
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"В ящике лежит много {self.item} {self.colors} различных цветов (поровну достаточно "
                 f"каждого). Их достают не глядя. Сколько предметов нужно достать, чтобы ГАРАНТИРОВАННО "
                 f"среди них оказалось {self.k} одного цвета?") if ru else
                (f"A drawer holds many {self.item} of {self.colors} different colors (plenty of each). "
                 f"They are drawn without looking. How many must be drawn to GUARANTEE {self.k} of the "
                 f"same color?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            (f"В худшем случае набираем по {self.k-1} каждого цвета: {self.colors}×{self.k-1} штук, "
             f"следующий предмет даёт {self.k} одного цвета." if ru else
             f"Worst case: {self.k-1} of each color, i.e. {self.colors}×{self.k-1}; one more forces {self.k} "
             f"of a color."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))


class MontyHallTask(_MiscBase):
    TASK_TYPE = "monty_hall"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        self.n = random.choice([3, 3, 3, 4, 5])
        # ведущий открывает одну козу; переключаемся на одну из оставшихся n-2 дверей
        self.prob = Fraction(self.n - 1, self.n * (self.n - 2)) if self.n > 2 else Fraction(0)
        self.value = float(self.prob)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        if self.n == 3:
            base = ("Классическая задача Монти Холла: 3 двери, за одной автомобиль, за двумя — козы. "
                    "Вы выбираете дверь, ведущий (знающий, где приз) открывает одну из оставшихся дверей "
                    "с козой. " if ru else
                    "Classic Monty Hall: 3 doors, a car behind one, goats behind two. You pick a door, the "
                    "host (who knows the prize) opens one of the other doors revealing a goat. ")
        else:
            base = (f"Обобщённая задача Монти Холла: {self.n} дверей, за одной автомобиль. Вы выбираете "
                    f"дверь, ведущий открывает ОДНУ из оставшихся дверей с козой. Затем вы переключаетесь "
                    f"на одну (случайную) из ещё закрытых дверей. " if ru else
                    f"Generalized Monty Hall: {self.n} doors, a car behind one. You pick a door, the host "
                    f"opens ONE other door revealing a goat. Then you switch to one (random) of the still-"
                    f"closed doors. ")
        q = ("Какова вероятность выиграть автомобиль, если переключиться? Ответьте дробью." if ru else
             "What is the probability of winning the car if you switch? Answer as a fraction.")
        return base + q

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Вероятность = P(изначально ошиблись) × P(переключение попадёт на приз)." if ru else
             "Probability = P(initial pick wrong) × P(switch lands on the prize)."),
            (f"Ответ: {self.prob.numerator}/{self.prob.denominator}." if ru else
             f"Answer: {self.prob.numerator}/{self.prob.denominator}."),
        ]
        self.final_answer = f"{self.prob.numerator}/{self.prob.denominator}"

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_value(prediction, self.value, tol=1e-2)


class AllenRelationsTask(_MiscBase):
    TASK_TYPE = "allen_relations"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}
    _SYN = {
        "before": ["before", "раньше", "до"],
        "after": ["after", "позже", "после"],
        "meets": ["meets", "встречает"],
        "met-by": ["met by", "met-by", "встречается после"],
        "overlaps": ["overlaps", "перекрывает"],
        "overlapped-by": ["overlapped by", "overlapped-by", "перекрывается"],
        "starts": ["starts", "начинает"],
        "started-by": ["started by", "started-by", "начинается вместе"],
        "during": ["during", "внутри", "во время"],
        "contains": ["contains", "содержит"],
        "finishes": ["finishes", "заканчивает"],
        "finished-by": ["finished by", "finished-by", "заканчивается вместе"],
        "equal": ["equal", "равно", "совпадает"],
    }
    _NAMES = list(_SYN.keys())

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _relation(self, a1, a2, b1, b2):
        if a2 < b1:
            return "before"
        if a1 > b2:
            return "after"
        if a2 == b1:
            return "meets"
        if a1 == b2:
            return "met-by"
        if a1 == b1 and a2 == b2:
            return "equal"
        if a1 == b1:
            return "starts" if a2 < b2 else "started-by"
        if a2 == b2:
            return "finishes" if a1 > b1 else "finished-by"
        if a1 < b1 and b2 < a2:
            return "contains"
        if b1 < a1 and a2 < b2:
            return "during"
        if a1 < b1 < a2 < b2:
            return "overlaps"
        if b1 < a1 < b2 < a2:
            return "overlapped-by"
        return "equal"

    def _build(self):
        for _ in range(200):
            a1 = random.randint(0, 8)
            a2 = a1 + random.randint(1, 6)
            b1 = random.randint(0, 8)
            b2 = b1 + random.randint(1, 6)
            self.A = (a1, a2)
            self.B = (b1, b2)
            self.rel = self._relation(a1, a2, b1, b2)
            if self.rel:
                return

    def _descr(self, language):
        ru = language == "ru"
        names = ", ".join(self._NAMES)
        return ((f"Даны два интервала времени: A = [{self.A[0]}, {self.A[1]}] и B = [{self.B[0]}, "
                 f"{self.B[1]}]. Определите отношение Аллена интервала A к интервалу B. Ответьте одним из "
                 f"английских названий: {names}.") if ru else
                (f"Two time intervals are given: A = [{self.A[0]}, {self.A[1]}] and B = [{self.B[0]}, "
                 f"{self.B[1]}]. Determine the Allen relation of A to B. Answer with one of: {names}."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Сравниваем концы интервалов, чтобы выбрать одно из 13 отношений Аллена." if ru else
             "Compare the interval endpoints to select one of the 13 Allen relations."),
            (f"Отношение A к B: {self.rel}." if ru else f"Relation of A to B: {self.rel}."),
        ]
        self.final_answer = self.rel

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        # выбираем отношение с самым длинным совпавшим синонимом (устраняем «before» ⊂ «...»)
        best, best_len = None, 0
        for rel, syns in self._SYN.items():
            for s in syns:
                if U.verify_label(prediction, [s]) == 1.0 and len(s) > best_len:
                    best, best_len = rel, len(s)
        return 1.0 if best == self.rel else 0.0
