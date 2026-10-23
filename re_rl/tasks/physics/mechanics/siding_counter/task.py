"""SidingCounterTask — вагоны и цепочка пружинных стрелок.

Стрелка 0 отправляет вагон в тупик и становится 1.
Стрелка 1 пропускает вагон дальше и становится 0.
Число вагонов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def switch_width(cars: int) -> int:
    width = 1
    while (1 << width) <= cars:
        width += 1
    return max(2, width)


def run_sidings(cars: int) -> Tuple[List[int], List[int], List[int]]:
    width = switch_width(cars)
    state = [0] * width
    flips = [0] * width
    exits = []
    for _ in range(cars):
        index = 0
        while state[index] == 1:
            state[index] = 0
            flips[index] += 1
            index += 1
        state[index] = 1
        flips[index] += 1
        exits.append(index + 1)
    return state, flips, exits


class SidingCounterTask(BaseMathTask):
    TASK_TYPE = "siding_counter"
    TASK_TYPES = ["bit", "exit"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 3},
        5: {"n": 4}, 6: {"n": 5}, 7: {"n": 6}, 8: {"n": 7},
        9: {"n": 8}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.width = switch_width(self.n)
        self.state, self.flips, self.exits = run_sidings(self.n)
        self.k = random.randint(1, self.width if self.task_type == "bit" else self.n)
        self.bit = self.state[self.k - 1] if self.task_type == "bit" else self.state[0]
        self.exit_at = self.exits[self.k - 1] if self.task_type == "exit" else self.exits[0]
        self.answer = self.bit if self.task_type == "bit" else self.exit_at
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "bit" else "s1"
        return texts.t(key, language, n=self.n, width=self.width, k=self.k)

    def solve(self):
        state = [0] * self.width
        steps = []
        for index in range(self.n):
            cursor = 0
            while state[cursor] == 1:
                state[cursor] = 0
                cursor += 1
            state[cursor] = 1
            shown = " ".join(str(bit) for bit in state)
            steps.append(texts.t("s2", self.language, i=index + 1, exit=cursor + 1, state=shown))
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
