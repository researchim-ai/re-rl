"""AveragePrecisionTask — средняя точность уже отсортированного списка.

Метки стоят от лучшей оценки к худшей. Точность в релевантной позиции i —
число релевантных среди первых i, делённое на i.
Средняя точность — среднее таких точностей. В списке есть хотя бы одна единица.
"""

import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.ml._exact import fmt_fraction, verify_fraction


def average_precision(labels: List[int]) -> Tuple[Fraction, Fraction]:
    hits = 0
    total = Fraction(0)
    last = Fraction(0)
    for index, label in enumerate(labels, start=1):
        if label:
            hits += 1
            last = Fraction(hits, index)
            total += last
    return total / hits, last


class AveragePrecisionTask(BaseMathTask):
    TASK_TYPE = "mean_average_precision"
    TASK_TYPES = ["ap", "last_precision"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7}, 9: {"n": 8}, 10: {"n": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.labels = [random.randint(0, 1) for _ in range(self.n)]
        if sum(self.labels) == 0:
            self.labels[0] = 1
        self.ap, self.last_precision = average_precision(self.labels)
        self.answer = self.ap if self.task_type == "ap" else self.last_precision
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        shown = " ".join(map(str, self.labels))
        rule = ((f"Метки уже стоят от лучшей оценки к худшей: {shown}. Единица — релевантный объект. "
                 f"Точность на позиции релевантного объекта — доля единиц от начала списка до него включительно. "
                 f"Средняя точность — среднее этих точностей. "
                 f"Ответ — целое или несократимая дробь.") if ru else
                (f"Labels are already ordered from the best score to the worst: {shown}. One means relevant. "
                 f"Precision at a relevant item is the fraction of ones from the start through that item. "
                 f"Average precision is the mean of those precisions. "
                 f"Answer with an integer or a reduced fraction."))
        ask = (("Найдите среднюю точность." if ru else "Find the average precision.")
               if self.task_type == "ap" else
               ("Найдите точность на последнем релевантном объекте." if ru else
                "Find the precision at the last relevant item."))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        shown = fmt_fraction(self.answer)
        step = ((f"Средняя точность {fmt_fraction(self.ap)}, "
                 f"на последнем релевантном {fmt_fraction(self.last_precision)}.") if ru else
                (f"Average precision {fmt_fraction(self.ap)}, "
                 f"at the last relevant item {fmt_fraction(self.last_precision)}."))
        self.solution_steps = [step, (f"Ответ: {shown}." if ru else f"Answer: {shown}.")]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return verify_fraction(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
