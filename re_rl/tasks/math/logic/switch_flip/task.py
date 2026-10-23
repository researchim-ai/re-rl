"""SwitchFlipTask — переключение тумблеров.

Каждая команда меняет один тумблер на противоположный. Тумблеров столько же, сколько команд.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def flip_trace(switches: int, toggles: Sequence[int]) -> Tuple[List[Tuple[int, int]], List[int]]:
    state = [0] * (switches + 1)
    ons = 0
    trace = []
    for index in toggles:
        if state[index]:
            state[index] = 0
            ons -= 1
        else:
            state[index] = 1
            ons += 1
        trace.append((state[index], ons))
    return trace, state


class SwitchFlipTask(BaseMathTask):
    TASK_TYPE = "switch_flip"
    TASK_TYPES = ["bit", "ons"]

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
        self.toggles = [random.randint(1, self.n) for _ in range(self.n)]
        self.trace, self.state = flip_trace(self.n, self.toggles)
        self.k = random.randint(1, self.n)
        self.bit = self.state[self.k]
        self.ons = self.trace[-1][1]
        self.answer = self.bit if self.task_type == "bit" else self.ons
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(index) for index in self.toggles)
        key = "s0" if self.task_type == "bit" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, switch=switch, bit=bit, ons=ons)
            for index, (switch, (bit, ons)) in enumerate(zip(self.toggles, self.trace), 1)
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
