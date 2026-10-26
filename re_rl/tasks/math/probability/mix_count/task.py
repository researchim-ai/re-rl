"""MixCountTask — вес числа успехов у испытаний с разными весами.

Каждое испытание умножает старые веса на вес неуспеха и на вес успеха.
Число испытаний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Trial = Tuple[int, int]


def mix_trace(trials: Sequence[Trial], target: int) -> List[Tuple[int, int]]:
    dist = {0: 1}
    trace = []
    for fail, success in trials:
        if fail < 1 or success < 1:
            raise RuntimeError("mass mismatch")
        nxt: Dict[int, int] = {}
        for count, weight in dist.items():
            nxt[count] = nxt.get(count, 0) + weight * fail
            nxt[count + 1] = nxt.get(count + 1, 0) + weight * success
        dist = nxt
        exact = dist.get(target, 0)
        peak = max(dist.values())
        trace.append((exact, peak))
    total = sum(dist.values())
    product = 1
    moment = sum(count * weight for count, weight in dist.items())
    identity = 0
    for fail, success in trials:
        product *= fail + success
    for fail, success in trials:
        identity += success * product // (fail + success)
    if total != product or moment != identity:
        raise RuntimeError("mass mismatch")
    return trace


class MixCountTask(BaseMathTask):
    TASK_TYPE = "mix_count"
    TASK_TYPES = ["exact", "peak"]

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
        self.trials = [(random.randint(1, 3), random.randint(1, 3)) for _ in range(self.n)]
        self.target = self.n // 2
        self.trace = mix_trace(self.trials, self.target)
        self.exact = self.trace[-1][0]
        self.peak = self.trace[-1][1]
        self.answer = self.exact if self.task_type == "exact" else self.peak
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{fail} {success}" for fail, success in self.trials)

    def _descr(self, language):
        key = "s0" if self.task_type == "exact" else "s1"
        return texts.t(key, language, n=self.n, listing=self._listing(), target=self.target)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, exact=exact, peak=peak)
            for index, (exact, peak) in enumerate(self.trace, 1)
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
