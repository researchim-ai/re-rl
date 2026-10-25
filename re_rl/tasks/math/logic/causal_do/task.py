"""CausalDoTask — вмешательство в треугольную структурную модель.

Каждая переменная зависит только от более ранней. Вмешательство заменяет её уравнение константой и пересчитывает потомков.
Наблюдение и вмешательство считаются отдельно, затем сравниваются.
Число переменных растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Rule = Tuple[int, int, int]


def causal_values(start: int, rules: Sequence[Rule], cut: int, bit: int) -> List[int]:
    values = [0, bit if cut == 1 else start]
    for index, (parent, op, noise) in enumerate(rules, 2):
        if index == cut:
            values.append(bit)
            continue
        parent_bit = values[parent]
        if op == 0:
            values.append(parent_bit)
        elif op == 1:
            values.append(1 - parent_bit)
        else:
            values.append(parent_bit ^ noise)
    return values


def causal_pair(start: int, rules: Sequence[Rule], cut: int, bit: int) -> List[Tuple[int, int, int]]:
    observed = causal_values(start, rules, 0, 0)
    changed = causal_values(start, rules, cut, bit)
    shift = 0
    trace = []
    for before, after in zip(observed[1:], changed[1:]):
        if before != after:
            shift += 1
        trace.append((before, after, shift))
    return trace


class CausalDoTask(BaseMathTask):
    TASK_TYPE = "causal_do"
    TASK_TYPES = ["shift", "after"]

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
        self.start = random.randint(0, 1)
        self.rules: List[Rule] = []
        for index in range(2, self.n + 1):
            parent = random.randint(1, index - 1)
            op = random.randint(0, 2)
            noise = random.randint(0, 1) if op == 2 else 0
            self.rules.append((parent, op, noise))
        observed = causal_values(self.start, self.rules, 0, 0)
        self.cut = random.randint(1, self.n)
        self.bit = 1 - observed[self.cut] if random.random() < 0.75 else observed[self.cut]
        self.trace = causal_pair(self.start, self.rules, self.cut, self.bit)
        self.shift = self.trace[-1][2]
        self.k = random.randint(1, self.n)
        self.after = self.trace[self.k - 1][1]
        self.answer = self.shift if self.task_type == "shift" else self.after
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rows = [f"1: {self.start}"]
        rows.extend(
            f"{index}: {parent} {op} {noise}"
            for index, (parent, op, noise) in enumerate(self.rules, 2)
        )
        key = "s0" if self.task_type == "shift" else "s1"
        return texts.t(
            key, language, n=self.n, rows="; ".join(rows), cut=self.cut, bit=self.bit, k=self.k,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, old=old, new=new, shift=shift)
            for index, (old, new, shift) in enumerate(self.trace, 1)
        ]
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
