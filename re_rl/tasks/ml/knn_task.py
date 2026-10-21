"""KNNClassifyTask — метод k ближайших соседей.

Расстояние манхэттенское, поэтому оно целое. Соседи упорядочиваются по
возрастанию расстояния, при равенстве — по меньшему номеру объекта (с 1).
k нечётное, классов два, так что голосование без ничьей.

Подтипы:
- ``label``   — класс запроса (A или B);
- ``nearest`` — номер ближайшего обучающего объекта.
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Point = Tuple[int, int, str]  # x, y, label


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(train: List[Point], query: Tuple[int, int], k: int) -> List[int]:
    """Индексы k ближайших (0-based), порядок по (расстояние, индекс)."""
    order = sorted(range(len(train)), key=lambda i: (manhattan((train[i][0], train[i][1]), query), i))
    return order[:k]


class KNNClassifyTask(BaseMathTask):
    TASK_TYPE = "knn_classify"
    TASK_TYPES = ["label", "nearest"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "k": 1, "span": 4}, 2: {"n": 5, "k": 1, "span": 5},
        3: {"n": 6, "k": 3, "span": 5}, 4: {"n": 7, "k": 3, "span": 6},
        5: {"n": 8, "k": 3, "span": 6}, 6: {"n": 9, "k": 3, "span": 7},
        7: {"n": 10, "k": 5, "span": 7}, 8: {"n": 11, "k": 5, "span": 8},
        9: {"n": 12, "k": 5, "span": 8}, 10: {"n": 14, "k": 5, "span": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.k = int(p["k"])
        self.span = int(p["span"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.k = min(self.k, self.n if self.n % 2 else self.n - 1)
        if self.k % 2 == 0:
            self.k -= 1
        self.k = max(1, self.k)
        self.train: List[Point] = []
        for _ in range(self.n):
            self.train.append((
                random.randint(-self.span, self.span),
                random.randint(-self.span, self.span),
                random.choice(["A", "B"]),
            ))
        self.query = (random.randint(-self.span, self.span), random.randint(-self.span, self.span))
        self.nn = neighbors(self.train, self.query, self.k)
        votes = {"A": 0, "B": 0}
        for i in self.nn:
            votes[self.train[i][2]] += 1
        self.label = "A" if votes["A"] > votes["B"] else "B"
        self.nearest_index = self.nn[0] + 1  # 1-based
        self.answer = self.label if self.task_type == "label" else self.nearest_index

    def _train_text(self) -> str:
        return ", ".join(f"{i + 1}: ({x}, {y}) {lab}" for i, (x, y, lab) in enumerate(self.train))

    def _descr(self, language):
        ru = language == "ru"
        data = self._train_text()
        qx, qy = self.query
        rule = (("Расстояние — манхэттенское |dx| + |dy|. При равенстве расстояний раньше "
                 "берётся объект с меньшим номером. k нечётное, побеждает большинство.")
                if ru else
                ("Distance is Manhattan |dx| + |dy|. Equal distances are broken by the smaller "
                 "object index. k is odd, so the majority class wins."))
        if self.task_type == "label":
            ask = ((f"Обучающая выборка: {data}. Запрос ({qx}, {qy}), k = {self.k}. "
                    f"Какой класс получит запрос? Ответьте A или B.") if ru else
                   (f"Training set: {data}. Query ({qx}, {qy}), k = {self.k}. "
                    f"Which class does the query get? Answer A or B."))
        else:
            ask = ((f"Обучающая выборка: {data}. Запрос ({qx}, {qy}). "
                    f"Какой номер у ближайшего объекта?") if ru else
                   (f"Training set: {data}. Query ({qx}, {qy}). "
                    f"What is the index of the nearest object?"))
        return f"{rule} {ask}"

    def solve(self):
        ru = self.language == "ru"
        bits = []
        for i in self.nn:
            x, y, lab = self.train[i]
            dist = manhattan((x, y), self.query)
            bits.append(f"{i + 1}/{lab}/d={dist}")
        if self.task_type == "label":
            step = ((f"Соседи (номер/класс/расстояние): {', '.join(bits)}. Класс {self.label}.")
                    if ru else
                    (f"Neighbors (index/class/distance): {', '.join(bits)}. Class {self.label}."))
            self.final_answer = self.label
        else:
            step = ((f"Ближайший — номер {self.nearest_index} (расстояния: {', '.join(bits)}).")
                    if ru else
                    (f"Nearest index is {self.nearest_index} (distances: {', '.join(bits)})."))
            self.final_answer = str(self.nearest_index)
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "label":
            return U.verify_label(prediction, [self.label])
        return U.verify_int(prediction, int(self.nearest_index))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
