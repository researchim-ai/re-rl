"""NafFireTask — стратифицированная программа с отрицанием по умолчанию.

Отрицание ссылается только на более ранний атом, поэтому устойчивая модель одна.
Её же даёт наименьшая модель редукта Гельфонда–Лифшица.
Число атомов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Rule = Tuple[int, int]


def naf_trace(fact: int, rules: Sequence[Rule]) -> Tuple[List[Tuple[int, int]], List[int]]:
    values = [0, fact]
    trues = fact
    trace = [(fact, trues)]
    for pos, neg in rules:
        bit = 1
        if pos and values[pos] == 0:
            bit = 0
        if neg and values[neg] == 1:
            bit = 0
        values.append(bit)
        trues += bit
        trace.append((bit, trues))
    return trace, values


def reduct_matches(fact: int, rules: Sequence[Rule], values: Sequence[int]) -> None:
    derived = set()
    if fact:
        derived.add(1)
    growing = True
    while growing:
        growing = False
        for index, (pos, neg) in enumerate(rules, 2):
            if index in derived:
                continue
            if neg and values[neg] == 1:
                continue
            if pos == 0 or pos in derived:
                derived.add(index)
                growing = True
    got = [1 if index in derived else 0 for index in range(1, len(values))]
    assert got == list(values[1:])


class NafFireTask(BaseMathTask):
    TASK_TYPE = "naf_fire"
    TASK_TYPES = ["trues", "here"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.fact = random.randint(0, 1)
        self.rules: List[Rule] = []
        for index in range(2, self.n + 1):
            kind = random.randint(0, 3)
            pos = random.randint(1, index - 1) if kind in (1, 3) else 0
            neg = random.randint(1, index - 1) if kind in (2, 3) else 0
            self.rules.append((pos, neg))
        self.trace, self.values = naf_trace(self.fact, self.rules)
        reduct_matches(self.fact, self.rules, self.values)
        self.trues = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.values[self.k]
        self.answer = self.trues if self.task_type == "trues" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{index}:{pos} {neg}" for index, (pos, neg) in enumerate(self.rules, 2))
        key = "s0" if self.task_type == "trues" else "s1"
        return texts.t(key, language, n=self.n, fact=self.fact, rules=shown, k=self.k)

    def solve(self):
        steps = [texts.t(
            "s2", self.language, i=1, pos=0, neg=0, bit=self.trace[0][0], trues=self.trace[0][1],
        )]
        for index, ((pos, neg), (bit, trues)) in enumerate(zip(self.rules, self.trace[1:]), 2):
            steps.append(texts.t(
                "s2", self.language, i=index, pos=pos, neg=neg, bit=bit, trues=trues,
            ))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
