"""ShapeRewardTask — формирование награды потенциалом.

Добавка равна потенциалу следующего состояния минус потенциал текущего.
Дисконт равен единице. Число переходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Jump = Tuple[int, int, int]


def shape_trace(potentials: Sequence[int], jumps: Sequence[Jump]) -> List[Tuple[int, int, int, int]]:
    total = 0
    bonus = 0
    trace = []
    for state, reward, nxt in jumps:
        extra = potentials[nxt] - potentials[state]
        shaped = reward + extra
        total += shaped
        bonus += extra
        trace.append((extra, shaped, total, bonus))
    return trace


class ShapeRewardTask(BaseMathTask):
    TASK_TYPE = "shape_reward"
    TASK_TYPES = ["total", "bonus"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "s": 3, "m": 4}, 2: {"n": 3, "s": 3, "m": 4},
        3: {"n": 4, "s": 3, "m": 4}, 4: {"n": 5, "s": 4, "m": 5},
        5: {"n": 6, "s": 4, "m": 5}, 6: {"n": 7, "s": 4, "m": 5},
        7: {"n": 8, "s": 4, "m": 6}, 8: {"n": 10, "s": 5, "m": 6},
        9: {"n": 12, "s": 5, "m": 6}, 10: {"n": 14, "s": 5, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = max(2, int(p["s"]))
        limit = max(1, int(p["m"]))
        self.potentials = [random.randint(-limit, limit) for _ in range(self.states)]
        self.jumps = [
            (random.randrange(self.states), random.randint(-limit, limit), random.randrange(self.states))
            for _ in range(self.n)
        ]
        self.trace = shape_trace(self.potentials, self.jumps)
        _, _, self.total, self.bonus = self.trace[-1]
        self.answer = self.total if self.task_type == "total" else self.bonus
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        potentials = ", ".join(str(value) for value in self.potentials)
        listing = "; ".join(
            f"{state + 1}, {reward}, {nxt + 1}" for state, reward, nxt in self.jumps
        )
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(
            key, language, states=self.states, n=self.n, potentials=potentials, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, state=state + 1, reward=reward, nxt=nxt + 1,
                extra=extra, shaped=shaped, total=total, bonus=bonus,
            )
            for index, ((state, reward, nxt), (extra, shaped, total, bonus)) in enumerate(
                zip(self.jumps, self.trace), 1,
            )
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
