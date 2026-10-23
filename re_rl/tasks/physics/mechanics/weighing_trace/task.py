"""WeighingTraceTask — поиск тяжёлой монеты по протоколу весов.

Каждое взвешивание сравнивает одну подозреваемую монету с эталоном.
Перевес оставляет одну возможность, равновесие её исключает.
Число взвешиваний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def follow_weighings(coins: Sequence[int], records: Sequence[Tuple[int, str]]) -> Tuple[int, int, List[Tuple[int, ...]]]:
    possible = set(coins)
    tipped = 0
    history = []
    for index, (coin, outcome) in enumerate(records, 1):
        if outcome == "down":
            possible = {coin}
            tipped = index
        else:
            possible.discard(coin)
        history.append(tuple(sorted(possible)))
    return next(iter(possible)), tipped, history


class WeighingTraceTask(BaseMathTask):
    TASK_TYPE = "weighing_trace"
    TASK_TYPES = ["heavy", "tipped"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.coins = list(range(1, self.n + 2))
        omitted = random.choice(self.coins)
        order = [coin for coin in self.coins if coin != omitted]
        random.shuffle(order)
        self.heavy = random.choice(self.coins)
        self.records = [(coin, "down" if coin == self.heavy else "balance") for coin in order]
        self.heavy, self.tipped, self.history = follow_weighings(self.coins, self.records)
        self.answer = self.heavy if self.task_type == "heavy" else self.tipped
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        coins = ", ".join(str(coin) for coin in self.coins)
        parts = []
        for index, (coin, outcome) in enumerate(self.records, 1):
            key = "s4" if outcome == "balance" else "s5"
            parts.append(texts.t(key, language, i=index, coin=coin))
        listing = "; ".join(parts)
        key = "s0" if self.task_type == "heavy" else "s1"
        return texts.t(key, language, coins=coins, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, suspects in enumerate(self.history, 1):
            shown = ", ".join(str(coin) for coin in suspects)
            steps.append(texts.t("s2", self.language, i=index, suspects=shown))
        steps.append(texts.t("s3", self.language, heavy=self.heavy, tipped=self.tipped))
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
