"""CouponCoverTask — момент, когда собраны все виды.

Лишние — сколько значений пришло после полного набора.
Длина ленты растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def coupon_trace(items: Sequence[int], kinds: int) -> List[Tuple[int, int, int]]:
    seen = set()
    cover = 0
    trace = []
    for index, item in enumerate(items, 1):
        seen.add(item)
        if cover == 0 and len(seen) == kinds:
            cover = index
        extra = index - cover if cover else 0
        trace.append((len(seen), cover, extra))
    return trace


class CouponCoverTask(BaseMathTask):
    TASK_TYPE = "coupon_cover"
    TASK_TYPES = ["cover", "extra"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "k": 2}, 2: {"n": 4, "k": 2}, 3: {"n": 5, "k": 2},
        4: {"n": 6, "k": 3}, 5: {"n": 7, "k": 3}, 6: {"n": 8, "k": 3},
        7: {"n": 10, "k": 4}, 8: {"n": 12, "k": 4}, 9: {"n": 14, "k": 5},
        10: {"n": 16, "k": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.kinds = max(1, int(p["k"]))
        self.items = [random.randint(1, self.kinds) for _ in range(self.n)]
        self.trace = coupon_trace(self.items, self.kinds)
        _, self.cover, self.extra = self.trace[-1]
        self.answer = self.cover if self.task_type == "cover" else self.extra
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.items)
        key = "s0" if self.task_type == "cover" else "s1"
        return texts.t(key, language, n=self.n, kinds=self.kinds, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, item=item, seen=seen, cover=cover, extra=extra)
            for index, (item, (seen, cover, extra)) in enumerate(zip(self.items, self.trace), 1)
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
