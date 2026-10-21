"""CosineRankTask — какой вектор ближе к запросу по косинусу.

Сравнение точное, без корней: знаки скалярных произведений учитываются отдельно,
а при одинаковом знаке сравниваются квадраты (dot^2 * норма другого).
Нулевые векторы и ничьи отбрасываются.

Подтипы: ближайший из A и B, скалярное произведение запроса с A.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Vec = Sequence[int]


def dot(a: Vec, b: Vec) -> int:
    return sum(x * y for x, y in zip(a, b))


def norm2(a: Vec) -> int:
    return sum(x * x for x in a)


def prefer(query: Vec, a: Vec, b: Vec) -> Optional[str]:
    """'A' или 'B', если косинус строго больше; None при ничьей или нулевом векторе."""
    if norm2(query) == 0 or norm2(a) == 0 or norm2(b) == 0:
        return None
    da, db = dot(query, a), dot(query, b)
    na, nb = norm2(a), norm2(b)
    if da >= 0 > db:
        return "A"
    if db >= 0 > da:
        return "B"
    left = da * da * nb
    right = db * db * na
    if da < 0 and db < 0:
        left, right = right, left
    if left > right:
        return "A"
    if right > left:
        return "B"
    return None


class CosineRankTask(BaseMathTask):
    TASK_TYPE = "cosine_rank"
    TASK_TYPES = ["nearest", "dot"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"dim": 2, "c": 3}, 2: {"dim": 2, "c": 3}, 3: {"dim": 2, "c": 4},
        4: {"dim": 3, "c": 3}, 5: {"dim": 3, "c": 4}, 6: {"dim": 3, "c": 4},
        7: {"dim": 3, "c": 5}, 8: {"dim": 4, "c": 4}, 9: {"dim": 4, "c": 5},
        10: {"dim": 4, "c": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.dim = int(p["dim"])
        self.c = int(p["c"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _vec(self) -> List[int]:
        for _ in range(20):
            v = [random.randint(-self.c, self.c) for _ in range(self.dim)]
            if norm2(v) > 0:
                return v
        return [1] + [0] * (self.dim - 1)

    def _build(self):
        self.query = self._vec()
        self.a = self._vec()
        self.b = self._vec()
        self.choice = prefer(self.query, self.a, self.b)
        for _ in range(30):
            if self.choice is not None:
                break
            self.b = self._vec()
            self.choice = prefer(self.query, self.a, self.b)
        if self.choice is None:
            self.a = list(self.query)
            self.b = [-x for x in self.query]
            self.choice = "A"
        self.dot_a = dot(self.query, self.a)

    def _fmt(self, v: Sequence[int]) -> str:
        return "(" + ", ".join(map(str, v)) + ")"

    def _descr(self, language):
        ru = language == "ru"
        data = ((f"Запрос q = {self._fmt(self.query)}, A = {self._fmt(self.a)}, B = {self._fmt(self.b)}.")
                if ru else
                (f"Query q = {self._fmt(self.query)}, A = {self._fmt(self.a)}, B = {self._fmt(self.b)}."))
        if self.task_type == "nearest":
            ask = (("Какой вектор ближе к q по косинусной близости? Ответьте A или B.") if ru else
                   ("Which vector is closer to q by cosine similarity? Answer A or B."))
        else:
            ask = (("Чему равно скалярное произведение q и A?") if ru else
                   ("What is the dot product of q and A?"))
        return f"{data} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "nearest":
            step = ((f"Ближе вектор {self.choice}.") if ru else f"Closer vector: {self.choice}.")
            self.final_answer = self.choice
        else:
            step = ((f"q·A = {self.dot_a}.") if ru else f"q·A = {self.dot_a}.")
            self.final_answer = str(self.dot_a)
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "nearest":
            return U.verify_label(prediction, [self.choice])
        return U.verify_int(prediction, self.dot_a)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
