"""SkipAddTask — остаточное прибавление по открытому вентилю.

Вентиль 1 прибавляет добавку к значению. Вентиль 0 оставляет значение прежним.
Число вентилей растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Step = Tuple[int, int]


def skip_trace(start: int, steps: Sequence[Step]) -> List[Tuple[int, int]]:
    value = start
    opens = 0
    trace = []
    for gate, delta in steps:
        if gate:
            value += delta
            opens += 1
        trace.append((value, opens))
    return trace


class SkipAddTask(BaseMathTask):
    TASK_TYPE = "skip_add"
    TASK_TYPES = ["value", "opens"]

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
        self.start = random.randint(0, 5)
        self.steps = [(random.randint(0, 1), random.randint(-3, 4)) for _ in range(self.n)]
        self.trace = skip_trace(self.start, self.steps)
        self.value = self.trace[-1][0]
        self.opens = self.trace[-1][1]
        self.answer = self.value if self.task_type == "value" else self.opens
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{gate} {delta}" for gate, delta in self.steps)
        key = "s0" if self.task_type == "value" else "s1"
        return texts.t(key, language, n=self.n, start=self.start, steps=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, gate=gate, delta=delta, value=value, opens=opens)
            for index, ((gate, delta), (value, opens)) in enumerate(zip(self.steps, self.trace), 1)
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
