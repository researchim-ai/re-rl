"""NaiveBayesTask — дискретный наивный Байес с лапласовским сглаживанием +1.

Два класса, A и B, два бинарных признака. Сравниваются точные дроби
P(класс) * P(x1|класс) * P(x2|класс). При равенстве побеждает A.

Подтипы:
- ``predict``     — предсказанный класс;
- ``conditional`` — одна условная вероятность со сглаживанием, как дробь.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction

Row = Tuple[int, int, str]  # x1, x2, class


def score(rows: List[Row], label: str, query: Tuple[int, int]) -> Fraction:
    n = len(rows)
    in_class = [r for r in rows if r[2] == label]
    nc = len(in_class)
    prior = Fraction(nc + 1, n + 2)
    total = prior
    for feat in (0, 1):
        matches = sum(1 for r in in_class if r[feat] == query[feat])
        total *= Fraction(matches + 1, nc + 2)
    return total


class NaiveBayesTask(BaseMathTask):
    TASK_TYPE = "naive_bayes"
    TASK_TYPES = ["predict", "conditional"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 6}, 2: {"n": 6}, 3: {"n": 8}, 4: {"n": 8}, 5: {"n": 10},
        6: {"n": 10}, 7: {"n": 12}, 8: {"n": 12}, 9: {"n": 14}, 10: {"n": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.rows = [(random.randint(0, 1), random.randint(0, 1), random.choice(["A", "B"]))
                     for _ in range(self.n)]
        if not any(r[2] == "A" for r in self.rows) or not any(r[2] == "B" for r in self.rows):
            self.rows[0] = (self.rows[0][0], self.rows[0][1], "A")
            self.rows[1] = (self.rows[1][0], self.rows[1][1], "B")
        self.query = (random.randint(0, 1), random.randint(0, 1))
        self.score_a = score(self.rows, "A", self.query)
        self.score_b = score(self.rows, "B", self.query)
        self.pred = "A" if self.score_a >= self.score_b else "B"
        # Условная вероятность: P(x1 = v | класс)
        self.cond_class = random.choice(["A", "B"])
        self.cond_value = random.randint(0, 1)
        in_class = [r for r in self.rows if r[2] == self.cond_class]
        matches = sum(1 for r in in_class if r[0] == self.cond_value)
        self.cond = Fraction(matches + 1, len(in_class) + 2)

    def _table(self) -> str:
        return ", ".join(f"({x1}, {x2}, {lab})" for x1, x2, lab in self.rows)

    def _descr(self, language):
        ru = language == "ru"
        rule = (("Наивный Байес, признаки бинарные, сглаживание Лапласа +1. "
                 "P(класс) = (n_класса + 1) / (N + 2), "
                 "P(признак=v | класс) = (число совпадений + 1) / (n_класса + 2). "
                 "При равных оценках выбирается класс A.") if ru else
                ("Naive Bayes, binary features, Laplace smoothing +1. "
                 "P(class) = (n_class + 1) / (N + 2), "
                 "P(feature=v | class) = (matches + 1) / (n_class + 2). "
                 "Equal scores go to class A."))
        data = self._table()
        if self.task_type == "predict":
            q = self.query
            ask = ((f"Обучающие тройки (x1, x2, класс): {data}. "
                    f"Какой класс у запроса ({q[0]}, {q[1]})? Ответьте A или B.") if ru else
                   (f"Training triples (x1, x2, class): {data}. "
                    f"Which class is predicted for ({q[0]}, {q[1]})? Answer A or B."))
        else:
            ask = ((f"Обучающие тройки (x1, x2, класс): {data}. "
                    f"Найдите P(x1 = {self.cond_value} | {self.cond_class}) со сглаживанием. "
                    f"Ответ — целое или несократимая дробь.") if ru else
                   (f"Training triples (x1, x2, class): {data}. "
                    f"Find P(x1 = {self.cond_value} | {self.cond_class}) with smoothing. "
                    f"Answer with an integer or a reduced fraction."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "predict":
            step = ((f"Оценка A = {fmt_fraction(self.score_a)}, B = {fmt_fraction(self.score_b)}.")
                    if ru else
                    (f"Score A = {fmt_fraction(self.score_a)}, B = {fmt_fraction(self.score_b)}."))
            self.final_answer = self.pred
        else:
            shown = fmt_fraction(self.cond)
            step = ((f"P(x1 = {self.cond_value} | {self.cond_class}) = {shown}.") if ru else
                    (f"P(x1 = {self.cond_value} | {self.cond_class}) = {shown}."))
            self.final_answer = shown
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "predict":
            return U.verify_label(prediction, [self.pred])
        return verify_fraction(prediction, self.cond)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
