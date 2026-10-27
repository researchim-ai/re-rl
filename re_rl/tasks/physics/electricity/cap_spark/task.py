"""CapSparkTask — пустые конденсаторы подключают к заряженному.

Заряд сохраняется, напряжение равно заряду, делённому на сумму ёмкостей.
Удвоенная энергия убывает: разница уходит в искру.
Число подключений растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

CHARGE = 720


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


def spark_trace(charge: int, first: int, extras: Sequence[int]) -> List[Tuple[int, int]]:
    if charge == 0 or first <= 0 or charge % first:
        raise RuntimeError("spark mismatch")
    capacity = first
    energy = charge * charge // capacity
    loss_sum = 0
    trace = []
    for extra in extras:
        if extra <= 0:
            raise RuntimeError("spark mismatch")
        capacity += extra
        if charge % capacity:
            raise RuntimeError("spark mismatch")
        voltage = charge // capacity
        new_energy = charge * charge // capacity
        loss = energy - new_energy
        if loss < 0:
            raise RuntimeError("spark mismatch")
        loss_sum += loss
        energy = new_energy
        trace.append((voltage, loss_sum))
    if loss_sum != charge * charge // first - energy:
        raise RuntimeError("spark mismatch")
    return trace


class CapSparkTask(BaseMathTask):
    TASK_TYPE = "cap_spark"
    TASK_TYPES = ["voltage", "loss"]

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
        self.charge = CHARGE
        self.first = 1
        self.extras = self._extras()
        self.trace = spark_trace(self.charge, self.first, self.extras)
        self.voltage = self.trace[-1][0]
        self.loss = self.trace[-1][1]
        self.answer = self.voltage if self.task_type == "voltage" else self.loss
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _extras(self) -> List[int]:
        capacity = self.first
        extras = []
        divisors = _divisors(CHARGE)
        for left in range(self.n, 0, -1):
            options = [item for item in divisors if item > capacity]
            if len(options) < left:
                raise RuntimeError("spark mismatch")
            total = random.choice(options[:len(options) - left + 1])
            extras.append(total - capacity)
            capacity = total
        return extras

    def _listing(self) -> str:
        return " ".join(str(extra) for extra in self.extras)

    def _descr(self, language):
        key = "s0" if self.task_type == "voltage" else "s1"
        return texts.t(
            key, language, n=self.n, charge=self.charge, first=self.first, listing=self._listing(),
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, voltage=voltage, loss=loss)
            for index, (voltage, loss) in enumerate(self.trace, 1)
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
