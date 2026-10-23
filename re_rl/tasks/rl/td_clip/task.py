"""TdClipTask — обрезка одношаговой TD-ошибки.

Ошибка равна награде плюс следующая оценка минус текущая. Затем она ограничивается.
Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int, int]


def td_clip_trace(rows: Sequence[Row], limit: int) -> List[Tuple[int, int, int, int]]:
    total = 0
    clips = 0
    trace = []
    for reward, value, nxt in rows:
        raw = reward + nxt - value
        clipped = raw
        if clipped > limit:
            clipped = limit
        elif clipped < -limit:
            clipped = -limit
        if clipped != raw:
            clips += 1
        total += clipped
        trace.append((raw, clipped, total, clips))
    return trace


class TdClipTask(BaseMathTask):
    TASK_TYPE = "td_clip"
    TASK_TYPES = ["total", "clips"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "c": 1, "m": 3}, 2: {"n": 3, "c": 1, "m": 4},
        3: {"n": 4, "c": 2, "m": 4}, 4: {"n": 5, "c": 2, "m": 5},
        5: {"n": 6, "c": 2, "m": 5}, 6: {"n": 7, "c": 2, "m": 6},
        7: {"n": 8, "c": 3, "m": 6}, 8: {"n": 10, "c": 3, "m": 6},
        9: {"n": 12, "c": 3, "m": 7}, 10: {"n": 14, "c": 3, "m": 7},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.limit = max(1, int(p["c"]))
        span = max(self.limit + 1, int(p["m"]))
        self.rows = [
            (random.randint(0, span), random.randint(0, span), random.randint(0, span))
            for _ in range(self.n)
        ]
        self.trace = td_clip_trace(self.rows, self.limit)
        _, _, self.total, self.clips = self.trace[-1]
        self.answer = self.total if self.task_type == "total" else self.clips
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{reward}, {value}, {nxt}" for reward, value, nxt in self.rows)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, limit=self.limit, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, raw=raw, clipped=clipped, total=total, clips=clips)
            for index, (raw, clipped, total, clips) in enumerate(self.trace, 1)
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
