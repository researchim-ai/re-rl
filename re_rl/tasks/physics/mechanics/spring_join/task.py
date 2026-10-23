"""SpringJoinTask — пружины ставят параллельно.

Жёсткости складываются, удлинение общее и равно силе, делённой на сумму жёсткостей.
Число пружин растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def join_trace(force: int, springs: Sequence[int]) -> List[Tuple[int, int]]:
    total = 0
    trace = []
    for stiffness in springs:
        total += stiffness
        trace.append((total, force // total))
    return trace


class SpringJoinTask(BaseMathTask):
    TASK_TYPE = "spring_join"
    TASK_TYPES = ["stiffness", "stretch"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(1, int(p["n"]))
        self.unit = random.randint(1, 4)
        self.sag = random.randint(1, 3)
        self.springs = [self.unit] * self.n
        self.force = self.unit * self.n * self.sag
        self.trace = join_trace(self.force, self.springs)
        self.stiffness, self.stretch = self.trace[-1]
        self.answer = self.stiffness if self.task_type == "stiffness" else self.stretch
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(item) for item in self.springs)
        key = "s0" if self.task_type == "stiffness" else "s1"
        return texts.t(key, language, n=self.n, force=self.force, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, stiffness=stiffness, stretch=stretch)
            for index, (stiffness, stretch) in enumerate(self.trace, 1)
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
