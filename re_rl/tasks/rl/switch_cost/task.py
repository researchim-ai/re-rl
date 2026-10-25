"""SwitchCostTask — награда минус плата за смену действия.

Первое действие смены не даёт. Каждая следующая смена вычитает единицу из суммы наград.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def switch_trace(rewards: Sequence[int], actions: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    switches = 0
    previous: Optional[int] = None
    trace = []
    for reward, action in zip(rewards, actions):
        if previous is not None and action != previous:
            switches += 1
        previous = action
        total += reward
        trace.append((switches, total, total - switches))
    return trace


class SwitchCostTask(BaseMathTask):
    TASK_TYPE = "switch_cost"
    TASK_TYPES = ["net", "switches"]

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
        self.rewards = [random.randint(0, 5) for _ in range(self.n)]
        self.actions = [random.randint(0, 1) for _ in range(self.n)]
        self.trace = switch_trace(self.rewards, self.actions)
        self.net = self.trace[-1][2]
        self.switches = self.trace[-1][0]
        self.answer = self.net if self.task_type == "net" else self.switches
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        rewards = ", ".join(str(reward) for reward in self.rewards)
        actions = ", ".join(str(action) for action in self.actions)
        key = "s0" if self.task_type == "net" else "s1"
        return texts.t(key, language, n=self.n, rewards=rewards, actions=actions)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, reward=reward, action=action,
                switches=switches, total=total, net=net,
            )
            for index, (reward, action, (switches, total, net)) in enumerate(
                zip(self.rewards, self.actions, self.trace), 1
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
