"""RankStopTask — правило секретаря на перестановке.

Первая доля кандидатов только задаёт порог. Дальше берётся первый, кто строго выше порога.
Длина очереди растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def secretary_trace(values: Sequence[int], reject: int) -> List[Tuple[int, int, int]]:
    best: Optional[int] = None
    chosen = 0
    seen = 0
    trace = []
    for index, value in enumerate(values):
        if chosen == 0:
            seen = index + 1
            if index < reject:
                best = value if best is None else max(best, value)
            elif value > best:
                chosen = value
        trace.append((0 if best is None else best, chosen, seen))
    return trace


class RankStopTask(BaseMathTask):
    TASK_TYPE = "rank_stop"
    TASK_TYPES = ["pick", "seen"]

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
        self.values = list(range(1, self.n + 1))
        random.shuffle(self.values)
        self.reject = max(1, self.n // 2)
        self.trace = secretary_trace(self.values, self.reject)
        self.pick = self.trace[-1][1]
        self.seen = self.trace[-1][2]
        self.answer = self.pick if self.task_type == "pick" else self.seen
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(value) for value in self.values)
        key = "s0" if self.task_type == "pick" else "s1"
        return texts.t(key, language, n=self.n, reject=self.reject, values=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, best=best, pick=pick, seen=seen)
            for index, (best, pick, seen) in enumerate(self.trace, 1)
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
