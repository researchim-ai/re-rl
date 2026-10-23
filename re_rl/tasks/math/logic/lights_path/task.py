"""LightsPathTask — погоня за лампочками.

Кнопка i переключает лампы i и i+1. Последняя кнопка переключает только свою лампу.
Матрица треугольная, поэтому набор нажатий однозначен. Число ламп растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def apply_presses(presses: Sequence[int]) -> List[int]:
    lights = [0] * len(presses)
    for index, press in enumerate(presses):
        if press:
            lights[index] ^= 1
            if index + 1 < len(lights):
                lights[index + 1] ^= 1
    return lights


def chase_presses(lights: Sequence[int]) -> Tuple[List[int], List[Tuple[int, ...]]]:
    state = list(lights)
    presses = []
    trace = []
    for index in range(len(state)):
        press = state[index]
        if press:
            state[index] ^= 1
            if index + 1 < len(state):
                state[index + 1] ^= 1
        presses.append(press)
        trace.append(tuple(state))
    return presses, trace


class LightsPathTask(BaseMathTask):
    TASK_TYPE = "lights_path"
    TASK_TYPES = ["presses", "at_k"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.presses = [random.randint(0, 1) for _ in range(self.n)]
        if sum(self.presses) == 0:
            self.presses[0] = 1
        self.lights = apply_presses(self.presses)
        self.recovered, self.trace = chase_presses(self.lights)
        self.k = random.randint(1, self.n)
        self.press_count = sum(self.presses)
        self.at_k = self.presses[self.k - 1]
        self.answer = self.press_count if self.task_type == "presses" else self.at_k
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        state = " ".join(str(bit) for bit in self.lights)
        key = "s0" if self.task_type == "presses" else "s1"
        return texts.t(key, language, n=self.n, state=state, k=self.k)

    def solve(self):
        steps = []
        for index, state in enumerate(self.trace, 1):
            shown = " ".join(str(bit) for bit in state)
            steps.append(texts.t(
                "s2", self.language, i=index, press=self.recovered[index - 1], state=shown,
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
