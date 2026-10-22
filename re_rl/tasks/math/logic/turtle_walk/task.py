"""TurtleWalkTask — путь по командам с поворотами на 90°.

Число команд растёт с уровнем. Итоговая точка зависит от текущего направления, его нельзя вынести из порядка команд.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_DIRS = ((1, 0), (0, 1), (-1, 0), (0, -1))


class TurtleWalkTask(BaseMathTask):
    TASK_TYPE = "turtle_walk"
    TASK_TYPES = ["x", "manhattan"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "d": 3}, 2: {"n": 2, "d": 4}, 3: {"n": 3, "d": 4},
        4: {"n": 4, "d": 5}, 5: {"n": 5, "d": 5}, 6: {"n": 6, "d": 6},
        7: {"n": 7, "d": 6}, 8: {"n": 8, "d": 7}, 9: {"n": 9, "d": 8},
        10: {"n": 10, "d": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = int(p["d"])
        heading = 0
        x = y = 0
        self.commands: List[Tuple[str, int]] = []
        self.trace: List[Tuple[int, int]] = []
        for _ in range(self.n):
            if random.random() < 0.65:
                dist = random.randint(1, limit)
                dx, dy = _DIRS[heading]
                x += dx * dist
                y += dy * dist
                self.commands.append(("F", dist))
            else:
                turn = random.choice(("L", "R"))
                heading = (heading + (1 if turn == "L" else -1)) % 4
                self.commands.append((turn, 0))
            self.trace.append((x, y))
        self.x, self.y = x, y
        self.manhattan = abs(x) + abs(y)
        self.answer = self.x if self.task_type == "x" else self.manhattan
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        parts = []
        for index, (kind, dist) in enumerate(self.commands, 1):
            token = kind if kind != "F" else f"F {dist}"
            parts.append(texts.t("s2", language, i=index, token=token))
        key = "s0" if self.task_type == "x" else "s1"
        return texts.t(key, language, n=self.n, listing=" ".join(parts))

    def solve(self):
        steps = []
        for index, ((kind, dist), (x, y)) in enumerate(zip(self.commands, self.trace), 1):
            token = kind if kind != "F" else f"F {dist}"
            steps.append(texts.t("s3", self.language, i=index, token=token, x=x, y=y))
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
