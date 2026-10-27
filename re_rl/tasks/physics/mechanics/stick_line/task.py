"""StickLineTask — цепочка неупругих ударов, тела слипаются.

Импульс сохраняется, удвоенная кинетическая энергия убывает.
Число ударов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

MOMENTUM = 720


def _divisors(number: int) -> List[int]:
    found = []
    probe = 1
    while probe * probe <= number:
        if number % probe == 0:
            found.append(probe)
            if probe * probe != number:
                found.append(number // probe)
        probe += 1
    return sorted(found)


def stick_trace(mass: int, speed: int, extras: Sequence[int]) -> List[Tuple[int, int]]:
    if mass <= 0 or speed == 0:
        raise RuntimeError("stick mismatch")
    momentum = mass * speed
    energy = mass * speed * speed
    initial_energy = energy
    loss_sum = 0
    trace = []
    for extra in extras:
        if extra <= 0:
            raise RuntimeError("stick mismatch")
        total = mass + extra
        if momentum % total:
            raise RuntimeError("stick mismatch")
        speed = momentum // total
        new_energy = total * speed * speed
        loss = energy - new_energy
        if loss < 0:
            raise RuntimeError("stick mismatch")
        loss_sum += loss
        energy = new_energy
        mass = total
        trace.append((speed, loss_sum))
    if energy + loss_sum != initial_energy or mass * speed != momentum:
        raise RuntimeError("stick mismatch")
    return trace


class StickLineTask(BaseMathTask):
    TASK_TYPE = "stick_line"
    TASK_TYPES = ["speed", "loss"]

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
        self.mass = 1
        self.speed = MOMENTUM
        self.extras = self._extras()
        self.trace = stick_trace(self.mass, self.speed, self.extras)
        self.final_speed = self.trace[-1][0]
        self.loss = self.trace[-1][1]
        initial = self.mass * self.speed * self.speed
        final_mass = self.mass + sum(self.extras)
        final_energy = final_mass * self.final_speed * self.final_speed
        if initial != final_energy + self.loss:
            raise RuntimeError("stick mismatch")
        self.answer = self.final_speed if self.task_type == "speed" else self.loss
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _extras(self) -> List[int]:
        mass = self.mass
        extras = []
        divisors = _divisors(MOMENTUM)
        for left in range(self.n, 0, -1):
            options = [item for item in divisors if item > mass]
            if len(options) < left:
                raise RuntimeError("stick mismatch")
            total = random.choice(options[:len(options) - left + 1])
            extras.append(total - mass)
            mass = total
        return extras

    def _listing(self) -> str:
        return " ".join(str(extra) for extra in self.extras)

    def _descr(self, language):
        key = "s0" if self.task_type == "speed" else "s1"
        return texts.t(
            key, language, n=self.n, mass=self.mass, speed=self.speed, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, loss=loss)
            for index, (speed, loss) in enumerate(self.trace, 1)
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
