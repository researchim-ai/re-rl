"""GroupVarTask — внутригрупповая и межгрупповая суммы квадратов.

Средние целые. Каждая точка добавляет квадрат отклонения от своего среднего и квадрат отклонения среднего от общего.
Число наблюдений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import defaultdict
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int]


def square_trace(pairs: Sequence[Pair]) -> List[Tuple[int, int]]:
    grouped: Dict[int, List[int]] = defaultdict(list)
    for group, value in pairs:
        grouped[group].append(value)
    means = {}
    for group, values in grouped.items():
        total = sum(values)
        if total % len(values) != 0:
            raise RuntimeError("group mismatch")
        means[group] = total // len(values)
    grand_sum = sum(value for _, value in pairs)
    if grand_sum % len(pairs) != 0:
        raise RuntimeError("group mismatch")
    grand = grand_sum // len(pairs)
    within = 0
    between = 0
    trace = []
    for group, value in pairs:
        within += (value - means[group]) ** 2
        between += (means[group] - grand) ** 2
        trace.append((within, between))
    total_ss = sum((value - grand) ** 2 for _, value in pairs)
    if total_ss != within + between:
        raise RuntimeError("group mismatch")
    return trace


class GroupVarTask(BaseMathTask):
    TASK_TYPE = "group_var"
    TASK_TYPES = ["within", "between"]

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
        self.pairs = self._observations()
        self.trace = square_trace(self.pairs)
        self.within = self.trace[-1][0]
        self.between = self.trace[-1][1]
        self.answer = self.within if self.task_type == "within" else self.between
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _deviations(self, count: int) -> List[int]:
        if count == 1:
            return [0]
        shifts = [random.randint(-2, 2) for _ in range(count - 1)]
        shifts.append(-sum(shifts))
        return shifts

    def _observations(self) -> List[Pair]:
        if self.n >= 6:
            first = random.randint(1, self.n - 2)
            second = random.randint(1, self.n - first - 1)
            counts = [first, second, self.n - first - second]
            grand = random.randint(0, 4)
            means = [grand + second, grand - first, grand]
        else:
            first = random.randint(1, self.n - 1)
            counts = [first, self.n - first]
            grand = random.randint(0, 4)
            means = [grand + counts[1], grand - first]
        pairs: List[Pair] = []
        for group, (count, mean) in enumerate(zip(counts, means)):
            for shift in self._deviations(count):
                pairs.append((group, mean + shift))
        random.shuffle(pairs)
        return pairs

    def _listing(self) -> str:
        return "; ".join(f"{group} {value}" for group, value in self.pairs)

    def _descr(self, language):
        key = "s0" if self.task_type == "within" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing())

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, within=within, between=between)
            for index, (within, between) in enumerate(self.trace, 1)
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
