"""CorridorKeysTask — комнаты по порядку, часть дверей закрыта ключом.

Число комнат растёт с уровнем. Ключ из ещё не открытой комнаты взять нельзя, поэтому путь обрывается на первом таком замке.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class CorridorKeysTask(BaseMathTask):
    TASK_TYPE = "corridor_keys"
    TASK_TYPES = ["farthest", "keys"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8}, 9: {"n": 9}, 10: {"n": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.need: List[Optional[int]] = [None] * self.n
        self.keys_here: List[List[int]] = [[] for _ in range(self.n)]
        for room in range(1, self.n):
            if random.random() < 0.65:
                self.need[room] = room
                self.keys_here[random.randrange(self.n)].append(room)
        held = set()
        self.farthest = 0
        self.stopped = False
        self.trace: List[Dict[str, int]] = []
        for room in range(self.n):
            if room and self.need[room] is not None and self.need[room] not in held:
                self.stopped = True
                self.trace.append({"room": room, "entered": 0, "held": len(held)})
                for later in range(room + 1, self.n):
                    self.trace.append({"room": later, "entered": 0, "held": len(held)})
                break
            held.update(self.keys_here[room])
            self.farthest = room
            self.trace.append({"room": room, "entered": 1, "held": len(held)})
        self.keys = len(held)
        self.answer = self.farthest if self.task_type == "farthest" else self.keys
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _room_text(self, language, room: int) -> str:
        lock = "-" if self.need[room] is None else str(self.need[room])
        keys = ",".join(str(item) for item in self.keys_here[room]) or "-"
        return texts.t("s2", language, i=room, lock=lock, keys=keys)

    def _descr(self, language):
        listing = " ".join(self._room_text(language, room) for room in range(self.n))
        key = "s0" if self.task_type == "farthest" else "s1"
        return texts.t(key, language, n=self.n, last=self.n - 1, listing=listing)

    def solve(self):
        steps = []
        for item in self.trace:
            state = texts.t("s5" if item["entered"] else "s6", self.language)
            steps.append(texts.t(
                "s3", self.language, room=item["room"], state=state, held=item["held"],
            ))
        steps.append(texts.t("s4", self.language, farthest=self.farthest, keys=self.keys))
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
