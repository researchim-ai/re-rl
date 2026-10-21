"""FractionalKnapsackTask — дробный рюкзак.

Стоимость каждого предмета кратна его массе (удельная стоимость — целое),
удельные стоимости попарно различны. Поэтому жадный порядок однозначен,
а оптимальная стоимость — целое число даже при разрезании последнего предмета.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def fractional_value(items: List[Tuple[int, int]], capacity: int) -> Tuple[int, List[Tuple[int, int, int]]]:
    """Возвращает стоимость и список (масса взятого, стоимость взятого, индекс).

    ``items`` — пары (масса, стоимость). При равной удельной стоимости раньше
    берётся меньший индекс; в генераторе удельные стоимости различны.
    """
    order = sorted(range(len(items)), key=lambda i: (-items[i][1] / items[i][0], i))
    left = capacity
    total = 0
    taken = []
    for i in order:
        if left <= 0:
            break
        w, v = items[i]
        take_w = min(w, left)
        take_v = v * take_w // w
        if v * take_w % w != 0:
            raise RuntimeError(texts.literal('literals.s3'))
        total += take_v
        left -= take_w
        taken.append((take_w, take_v, i))
    return total, taken


class FractionalKnapsackTask(BaseMathTask):
    TASK_TYPE = "fractional_knapsack"
    TASK_TYPES = ["value"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5}, 9: {"n": 6}, 10: {"n": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.difficulty = difficulty
        self.task_type = "value"
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        densities = sorted(random.sample(range(1, 14), self.n), reverse=True)
        weights = [random.randint(2, 8) for _ in range(self.n)]
        self.items = [(w, d * w) for w, d in zip(weights, densities)]
        order = sorted(range(self.n), key=lambda i: (-densities[i], i))
        # Чаще оставляем последний взятый предмет разрезанным.
        if self.difficulty <= 2 and random.random() < 0.5:
            self.capacity = sum(weights)
        else:
            n_full = random.randint(0, self.n - 1)
            full_w = sum(weights[order[i]] for i in range(n_full))
            w_next = weights[order[n_full]]
            self.capacity = full_w + random.randint(1, w_next - 1)
        self.answer, self.taken = fractional_value(self.items, self.capacity)

    def _descr(self, language):
        items = ", ".join(f"({w}, {v})" for w, v in self.items)
        return ((texts.t('s0', language, items=items, capacity=self.capacity)))

    def solve(self):
        bits = []
        for take_w, take_v, i in self.taken:
            w, v = self.items[i]
            bits.append((texts.t('s2', self.language, v0=i + 1, take_w=take_w, w=w, take_v=take_v)))
        self.solution_steps = [
            ((texts.t('s1', self.language, v0='; '.join(bits)))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
