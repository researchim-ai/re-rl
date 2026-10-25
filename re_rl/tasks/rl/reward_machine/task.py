"""RewardMachineTask — награда по фазам автомата.

Фаза 0 ждёт событие 1. Фаза 1 ждёт событие 2 и тогда даёт 4. Фаза 2 на каждом событии даёт 1.
Число событий растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def machine_trace(events: Sequence[int]) -> List[Tuple[int, int, int]]:
    phase = 0
    total = 0
    trace = []
    for event in events:
        reward = 0
        if phase == 0 and event == 1:
            phase = 1
        elif phase == 1 and event == 2:
            phase = 2
            reward = 4
        elif phase == 2:
            reward = 1
        total += reward
        trace.append((phase, reward, total))
    return trace


class RewardMachineTask(BaseMathTask):
    TASK_TYPE = "reward_machine"
    TASK_TYPES = ["reward", "phase"]

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
        self.events = [random.randint(0, 2) for _ in range(self.n)]
        self.trace = machine_trace(self.events)
        self.reward = self.trace[-1][2]
        self.phase = self.trace[-1][0]
        self.answer = self.reward if self.task_type == "reward" else self.phase
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(event) for event in self.events)
        key = "s0" if self.task_type == "reward" else "s1"
        return texts.t(key, language, n=self.n, events=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, event=event, phase=phase, reward=reward, total=total)
            for index, (event, (phase, reward, total)) in enumerate(zip(self.events, self.trace), 1)
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
