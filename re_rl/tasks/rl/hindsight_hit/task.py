"""HindsightHitTask — пересчёт наград с достигнутой целью.

Исходная цель задана заранее. После прохода целью становится последнее состояние, и попадания считаются заново.
Число состояний растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def hindsight_trace(states: Sequence[int], goal: int) -> List[Tuple[int, int]]:
    final = states[-1]
    original = 0
    revised = 0
    trace = []
    for state in states:
        if state == goal:
            original += 1
        if state == final:
            revised += 1
        trace.append((original, revised))
    return trace


class HindsightHitTask(BaseMathTask):
    TASK_TYPE = "hindsight_hit"
    TASK_TYPES = ["original", "revised"]

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
        self.states = [random.randint(0, self.n) for _ in range(self.n)]
        self.goal = random.randint(0, self.n)
        self.trace = hindsight_trace(self.states, self.goal)
        self.original = self.trace[-1][0]
        self.revised = self.trace[-1][1]
        self.answer = self.original if self.task_type == "original" else self.revised
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(state) for state in self.states)
        key = "s0" if self.task_type == "original" else "s1"
        return texts.t(key, language, n=self.n, states=shown, goal=self.goal)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, state=state, original=original, revised=revised)
            for index, (state, (original, revised)) in enumerate(zip(self.states, self.trace), 1)
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
