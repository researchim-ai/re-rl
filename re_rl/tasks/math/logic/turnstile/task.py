"""TurnstileTask — турникет с монетой и толчком.

Закрытый турникет открывается монетой. Открытый пропускает толчок и снова закрывается. Лишние действия ничего не делают.
Число действий растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def stile_trace(events: Sequence[int]) -> List[Tuple[int, int]]:
    unlocked = 0
    entries = 0
    trace = []
    for event in events:
        if unlocked == 0 and event == 0:
            unlocked = 1
        elif unlocked == 1 and event == 1:
            unlocked = 0
            entries += 1
        trace.append((unlocked, entries))
    return trace


class TurnstileTask(BaseMathTask):
    TASK_TYPE = "turnstile"
    TASK_TYPES = ["entries", "state"]

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
        self.events = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = stile_trace(self.events)
        self.entries = self.trace[-1][1]
        self.state = self.trace[-1][0]
        self.answer = self.entries if self.task_type == "entries" else self.state
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(event) for event in self.events)
        key = "s0" if self.task_type == "entries" else "s1"
        return texts.t(key, language, n=self.n, events=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, event=event, state=state, entries=entries)
            for index, (event, (state, entries)) in enumerate(zip(self.events, self.trace), 1)
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
