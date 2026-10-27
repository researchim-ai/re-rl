"""BurstSplitTask — цепочка распадов с сохранением импульса.

От тела отрывается осколок с заданной массой и скоростью. Скорость остатка определяется импульсом.
Удвоенная кинетическая энергия растёт на энергию взрыва.
Число распадов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Piece = Tuple[int, int]


def burst_trace(mass: int, speed: int, pieces: Sequence[Piece]) -> List[Tuple[int, int]]:
    if mass <= 0:
        raise RuntimeError("burst mismatch")
    released_sum = 0
    trace = []
    for frag, frag_speed in pieces:
        rest = mass - frag
        if frag <= 0 or rest <= 0:
            raise RuntimeError("burst mismatch")
        momentum = mass * speed - frag * frag_speed
        if momentum % rest:
            raise RuntimeError("burst mismatch")
        new_speed = momentum // rest
        before = mass * speed * speed
        after = rest * new_speed * new_speed + frag * frag_speed * frag_speed
        released = after - before
        if released < 0:
            raise RuntimeError("burst mismatch")
        released_sum += released
        trace.append((new_speed, released_sum))
        mass = rest
        speed = new_speed
    return trace


class BurstSplitTask(BaseMathTask):
    TASK_TYPE = "burst_split"
    TASK_TYPES = ["speed", "blast"]

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
        self.mass = 3 * self.n + 1
        self.speed = self.mass
        self.pieces = self._pieces()
        self.trace = burst_trace(self.mass, self.speed, self.pieces)
        self.final_speed = self.trace[-1][0]
        self.blast = self.trace[-1][1]
        self.answer = self.final_speed if self.task_type == "speed" else self.blast
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pieces(self) -> List[Piece]:
        mass = self.mass
        speed = self.speed
        pieces = []
        for _ in range(self.n):
            high = min(3, mass - 1, speed - 1)
            frag = random.randint(1, high)
            rest = mass - frag
            frag_speed = speed + rest
            pieces.append((frag, frag_speed))
            speed -= frag
            mass = rest
        return pieces

    def _listing(self) -> str:
        return "; ".join(f"{frag} {frag_speed}" for frag, frag_speed in self.pieces)

    def _descr(self, language):
        key = "s0" if self.task_type == "speed" else "s1"
        return texts.t(
            key, language, n=self.n, mass=self.mass, speed=self.speed, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, blast=blast)
            for index, (speed, blast) in enumerate(self.trace, 1)
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
