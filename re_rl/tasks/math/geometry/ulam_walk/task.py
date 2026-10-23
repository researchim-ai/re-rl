"""UlamWalkTask — квадратная спираль на клетчатой плоскости.

Сначала шаг на восток, затем на север, потом ноги по два шага и дальше длиннее на 1 каждые два поворота.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ulam_trace(steps: int) -> List[Tuple[int, int]]:
    x = 0
    y = 0
    dirs = ((1, 0), (0, 1), (-1, 0), (0, -1))
    facing = 0
    leg = 1
    left = 1
    pair = 0
    trace = []
    for _ in range(steps):
        dx, dy = dirs[facing]
        x += dx
        y += dy
        left -= 1
        if left == 0:
            facing = (facing + 1) % 4
            pair += 1
            if pair == 2:
                leg += 1
                pair = 0
            left = leg
        trace.append((x, y))
    return trace


class UlamWalkTask(BaseMathTask):
    TASK_TYPE = "ulam_walk"
    TASK_TYPES = ["x", "manhattan"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 6},
        5: {"n": 8}, 6: {"n": 10}, 7: {"n": 12}, 8: {"n": 14},
        9: {"n": 16}, 10: {"n": 20},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.trace = ulam_trace(self.n)
        self.x, self.y = self.trace[-1]
        self.manhattan = abs(self.x) + abs(self.y)
        self.answer = self.x if self.task_type == "x" else self.manhattan
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "x" else "s1"
        return texts.t(key, language, n=self.n)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, x=x, y=y)
            for index, (x, y) in enumerate(self.trace, 1)
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
