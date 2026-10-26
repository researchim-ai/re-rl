"""RepeatTestTask — сколько больных остаётся после цепочки тестов.

Если числа не делятся на делитель теста, оба сначала умножаются на него: доля не меняется.
Число тестов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Test = Tuple[int, int, int]


def confirm_trace(sick: int, healthy: int, tests: Sequence[Test]) -> List[Tuple[int, int]]:
    trace = []
    for den, hit, miss in tests:
        if den < 1 or not 1 <= hit <= den or not 0 <= miss <= den:
            raise RuntimeError("test mismatch")
        scale = den if sick % den or healthy % den else 1
        if (sick * scale * hit) % den or (healthy * scale * miss) % den:
            raise RuntimeError("test mismatch")
        sick = sick * scale * hit // den
        healthy = healthy * scale * miss // den
        if sick + healthy <= 0:
            raise RuntimeError("test mismatch")
        trace.append((sick, sick + healthy))
    return trace


class RepeatTestTask(BaseMathTask):
    TASK_TYPE = "repeat_test"
    TASK_TYPES = ["sick", "positives"]

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
        self.sick = random.randint(2, 6)
        self.healthy = random.randint(2, 6)
        sick, healthy = self.sick, self.healthy
        self.tests: List[Test] = []
        for _ in range(self.n):
            den = random.randint(2, 5)
            hit = random.randint(1, den)
            miss = random.randint(0, den)
            self.tests.append((den, hit, miss))
            scale = den if sick % den or healthy % den else 1
            sick = sick * scale * hit // den
            healthy = healthy * scale * miss // den
        self.trace = confirm_trace(self.sick, self.healthy, self.tests)
        self.final_sick = self.trace[-1][0]
        self.positives = self.trace[-1][1]
        self.answer = self.final_sick if self.task_type == "sick" else self.positives
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _listing(self) -> str:
        return "; ".join(f"{den} {hit} {miss}" for den, hit, miss in self.tests)

    def _descr(self, language):
        key = "s0" if self.task_type == "sick" else "s1"
        return texts.t(
            key, language, n=self.n, sick=self.sick, healthy=self.healthy, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, sick=sick, positives=positives)
            for index, (sick, positives) in enumerate(self.trace, 1)
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
