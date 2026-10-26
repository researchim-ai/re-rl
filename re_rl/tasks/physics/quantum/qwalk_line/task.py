"""QwalkLineTask — дискретное квантовое блуждание на прямой.

Монета (правая, левая) переходит в (правая+левая, правая-левая), затем правая
сдвигается вправо, а левая влево. Сумма весов удваивается на каждом шаге.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Coin = Tuple[int, int]


def qwalk_trace(right: int, left: int, steps: int) -> List[Tuple[int, int]]:
    state = {0: (right, left)}
    start_mass = right * right + left * left
    trace = []
    for step in range(1, steps + 1):
        coined = {place: (one + other, one - other) for place, (one, other) in state.items()}
        shifted: Dict[int, Coin] = {}
        for place, (one, other) in coined.items():
            stay_right, stay_left = shifted.get(place + 1, (0, 0))
            shifted[place + 1] = (stay_right + one, stay_left)
            stay_right, stay_left = shifted.get(place - 1, (0, 0))
            shifted[place - 1] = (stay_right, stay_left + other)
        state = {place: coin for place, coin in shifted.items() if coin != (0, 0)}
        center_right, center_left = state.get(0, (0, 0))
        center = center_right * center_right + center_left * center_left
        mass = sum(one * one + other * other for one, other in state.values())
        if mass != start_mass * (1 << step):
            raise RuntimeError("mass mismatch")
        trace.append((center, mass))
    return trace


class QwalkLineTask(BaseMathTask):
    TASK_TYPE = "qwalk_line"
    TASK_TYPES = ["center", "mass"]
    STARTS = ((1, 0), (0, 1), (1, 1), (1, -1))

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
        self.right, self.left = random.choice(self.STARTS)
        self.trace = qwalk_trace(self.right, self.left, self.n)
        self.center = self.trace[-1][0]
        self.mass = self.trace[-1][1]
        self.answer = self.center if self.task_type == "center" else self.mass
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "center" else "s1"
        return texts.t(key, language, n=self.n, right=self.right, left=self.left)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, center=center, mass=mass)
            for index, (center, mass) in enumerate(self.trace, 1)
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
