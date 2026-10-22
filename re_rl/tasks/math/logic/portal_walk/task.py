"""PortalWalkTask — переход по комнатам заданное число раз.

Число шагов растёт с уровнем. Следующая комната читается из таблицы текущей, сократить путь формулой нельзя.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class PortalWalkTask(BaseMathTask):
    TASK_TYPE = "portal_walk"
    TASK_TYPES = ["room"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "rooms": 3}, 2: {"n": 3, "rooms": 3}, 3: {"n": 4, "rooms": 4},
        4: {"n": 4, "rooms": 4}, 5: {"n": 5, "rooms": 5}, 6: {"n": 6, "rooms": 5},
        7: {"n": 8, "rooms": 6}, 8: {"n": 9, "rooms": 6}, 9: {"n": 10, "rooms": 7},
        10: {"n": 12, "rooms": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = "room"
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.rooms = max(2, int(p["rooms"]))
        self.nxt: List[int] = [random.randint(0, self.rooms - 1) for _ in range(self.rooms)]
        self.trace: List[int] = [0]
        room = 0
        for _ in range(self.n):
            room = self.nxt[room]
            self.trace.append(room)
        self.answer = room
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(f"{index}→{target}" for index, target in enumerate(self.nxt))
        return texts.t("s0", language, last=self.rooms - 1, listing=listing, n=self.n)

    def solve(self):
        steps = []
        for index in range(1, len(self.trace)):
            steps.append(texts.t(
                "s1", self.language, i=index, prev=self.trace[index - 1], room=self.trace[index],
            ))
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
