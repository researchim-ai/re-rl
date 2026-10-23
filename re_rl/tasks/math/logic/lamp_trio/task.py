"""LampTrioTask — нажатие переключает лампу и обоих соседей.

Крайняя лампа не имеет соседа за краем. В начале все лампы погашены.
Число ламп и нажатий растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def lamp_trace(lamps: int, presses: Sequence[int]) -> Tuple[List[Tuple[int, int]], List[int]]:
    state = [0] * lamps
    trace = []
    for press in presses:
        for index in (press - 2, press - 1, press):
            if 0 <= index < lamps:
                state[index] ^= 1
        trace.append((state[press - 1], sum(state)))
    return trace, state


class LampTrioTask(BaseMathTask):
    TASK_TYPE = "lamp_trio"
    TASK_TYPES = ["ons", "bit"]

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
        self.presses = [random.randint(1, self.n) for _ in range(self.n)]
        self.trace, self.state = lamp_trace(self.n, self.presses)
        self.ons = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.bit = self.state[self.k - 1]
        self.answer = self.ons if self.task_type == "ons" else self.bit
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        presses = ", ".join(str(press) for press in self.presses)
        key = "s0" if self.task_type == "ons" else "s1"
        return texts.t(key, language, n=self.n, presses=presses, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, press=press, bit=bit, ons=ons)
            for index, (press, (bit, ons)) in enumerate(zip(self.presses, self.trace), 1)
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
