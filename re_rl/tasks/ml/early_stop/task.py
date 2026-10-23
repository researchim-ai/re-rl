"""EarlyStopTask — ранняя остановка по терпению.

Лучшая потеря обновляется только при строгом улучшении. Иначе счётчик ожидания растёт.
Число эпох растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stop_trace(losses: Sequence[int], patience: int) -> List[Tuple[int, int, int]]:
    best: Optional[int] = None
    wait = 0
    stop = 0
    trace = []
    for loss in losses:
        if best is None or loss < best:
            best = loss
            wait = 0
        else:
            wait += 1
        if stop == 0 and wait >= patience:
            stop = len(trace) + 1
        trace.append((best, wait, stop))
    return trace


class EarlyStopTask(BaseMathTask):
    TASK_TYPE = "early_stop"
    TASK_TYPES = ["best", "stop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "p": 2}, 2: {"n": 4, "p": 2}, 3: {"n": 5, "p": 2},
        4: {"n": 6, "p": 2}, 5: {"n": 7, "p": 2}, 6: {"n": 8, "p": 3},
        7: {"n": 9, "p": 3}, 8: {"n": 10, "p": 3}, 9: {"n": 12, "p": 3},
        10: {"n": 14, "p": 3},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.patience = max(1, int(p["p"]))
        self.losses = [random.randint(0, 9) for _ in range(self.n)]
        self.trace = stop_trace(self.losses, self.patience)
        self.best, _, self.stop = self.trace[-1]
        self.answer = self.best if self.task_type == "best" else self.stop
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(loss) for loss in self.losses)
        key = "s0" if self.task_type == "best" else "s1"
        return texts.t(key, language, n=self.n, patience=self.patience, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, loss=loss, best=best, wait=wait, stop=stop)
            for index, (loss, (best, wait, stop)) in enumerate(zip(self.losses, self.trace), 1)
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
