"""Календарные рассуждения: день недели по дате, разница дат в днях, день недели
через N дней. Эталон вычисляется через datetime.date (детерминированно)."""

import datetime
import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_WD = {
    "ru": ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"],
    "en": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
}


class CalendarReasoningTask(BaseMathTask):
    TASK_TYPE = "calendar_reasoning"
    TASK_TYPES = ["day_of_week", "date_diff", "add_days"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"span": 30}, 2: {"span": 90}, 3: {"span": 180}, 4: {"span": 365},
        5: {"span": 730}, 6: {"span": 1500}, 7: {"span": 3000}, 8: {"span": 6000},
        9: {"span": 12000}, 10: {"span": 25000},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.span = int(p["span"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.lang = language if language in _WD else "en"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rand_date(self):
        base = datetime.date(2000, 1, 1)
        return base + datetime.timedelta(days=random.randint(0, 20000))

    def _build(self):
        self.d1 = self._rand_date()
        if self.subtype == "day_of_week":
            self.answer_label = _WD[self.lang][self.d1.weekday()]
        elif self.subtype == "date_diff":
            self.d2 = self.d1 + datetime.timedelta(days=random.randint(1, self.span))
            self.answer_int = (self.d2 - self.d1).days
        else:  # add_days
            self.delta = random.randint(1, self.span)
            self.answer_label = _WD[self.lang][(self.d1 + datetime.timedelta(days=self.delta)).weekday()]

    @staticmethod
    def _fmt(d):
        return d.strftime("%Y-%m-%d")

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "day_of_week":
            return ((f"Какой день недели приходится на дату {self._fmt(self.d1)}? "
                     f"Ответьте названием дня недели.") if ru else
                    (f"What day of the week is {self._fmt(self.d1)}? Answer with the weekday name."))
        if self.subtype == "date_diff":
            return ((f"Сколько дней между датами {self._fmt(self.d1)} и {self._fmt(self.d2)}?") if ru else
                    (f"How many days are there between {self._fmt(self.d1)} and {self._fmt(self.d2)}?"))
        return ((f"Дата {self._fmt(self.d1)}. Какой день недели будет через {self.delta} дней? "
                 f"Ответьте названием дня недели.") if ru else
                (f"The date is {self._fmt(self.d1)}. What weekday is it {self.delta} days later? "
                 f"Answer with the weekday name."))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "date_diff":
            self.solution_steps = [
                ("Считаем число дней между датами (с учётом високосных годов)." if ru else
                 "Count the number of days between the dates (accounting for leap years)."),
                (f"Разница = {self.answer_int} дней." if ru else f"Difference = {self.answer_int} days."),
            ]
            self.final_answer = str(self.answer_int)
        else:
            self.solution_steps = [
                ("Определяем день недели по календарю." if ru else
                 "Determine the weekday from the calendar."),
                (f"Ответ: {self.answer_label}." if ru else f"Answer: {self.answer_label}."),
            ]
            self.final_answer = self.answer_label

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "date_diff":
            return U.verify_int(prediction, int(self.answer_int))
        # принимаем название дня недели на обоих языках
        idx = _WD[self.lang].index(self.answer_label)
        return U.verify_label(prediction, [_WD["ru"][idx], _WD["en"][idx]])

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
