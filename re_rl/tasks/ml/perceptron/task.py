"""PerceptronUpdateTask — обновление перцептрона.

Метки y равны +1 или -1. Правило, если y * (w·x + b) <= 0:
w := w + y*x, b := b + y. Иначе веса не меняются.

Подтипы:
- ``one``   — веса после одного примера;
- ``epoch`` — веса после одного прохода по выборке.

Ответ — три целых: w1, w2, b.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Example = Tuple[int, int, int]  # x1, x2, y


def perceptron_step(w: List[int], b: int, ex: Example) -> Tuple[List[int], int, bool]:
    x1, x2, y = ex
    activation = y * (w[0] * x1 + w[1] * x2 + b)
    if activation <= 0:
        return [w[0] + y * x1, w[1] + y * x2], b + y, True
    return list(w), b, False


class PerceptronUpdateTask(BaseMathTask):
    TASK_TYPE = "perceptron_update"
    TASK_TYPES = ["one", "epoch"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 1, "coord": 2}, 2: {"m": 1, "coord": 2}, 3: {"m": 2, "coord": 2},
        4: {"m": 3, "coord": 3}, 5: {"m": 3, "coord": 3}, 6: {"m": 4, "coord": 3},
        7: {"m": 4, "coord": 3}, 8: {"m": 5, "coord": 4}, 9: {"m": 5, "coord": 4},
        10: {"m": 6, "coord": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.m = int(p["m"])
        self.coord = int(p["coord"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        count = 1 if self.task_type == "one" else self.m
        self.examples: List[Example] = []
        for _ in range(count):
            self.examples.append((
                random.randint(-self.coord, self.coord),
                random.randint(-self.coord, self.coord),
                random.choice([-1, 1]),
            ))
        self.w0 = [random.randint(-1, 1), random.randint(-1, 1)]
        self.b0 = random.randint(-1, 1)
        self.trace = []
        w, b = list(self.w0), self.b0
        for ex in self.examples:
            w, b, updated = perceptron_step(w, b, ex)
            self.trace.append((ex, list(w), b, updated))
        self.w, self.b = w, b
        self.answer = [w[0], w[1], b]

    def _ex_text(self) -> str:
        return ", ".join(f"({x1}, {x2}, y={y})" for x1, x2, y in self.examples)

    def _descr(self, language):
        rule = ((texts.t('s0', language)))
        data = self._ex_text()
        head = ((texts.t('s1', language, v0=self.w0[0], v1=self.w0[1], b0=self.b0, data=data)))
        ask = ((texts.t('s2', language)))
        return f"{rule} {head} {ask}"

    def solve(self):
        bits = []
        for (x1, x2, y), w, b, updated in self.trace:
            mark = (texts.t('s3', self.language) if updated else texts.t('s4', self.language))
            bits.append(f"({x1}, {x2}, y={y}) -> ({w[0]}, {w[1]}, {b}), {mark}")
        shown = f"{self.w[0]}, {self.w[1]}, {self.b}"
        self.solution_steps = [
            (((texts.t('s5', self.language))) + "; ".join(bits) + "."),
            ((texts.common('answer_line', self.language, answer=shown))),
        ]
        self.final_answer = shown

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int_sequence(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
