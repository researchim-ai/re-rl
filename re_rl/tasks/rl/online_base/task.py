"""OnlineBaseTask — преимущество относительно среднего прошлых наград.

База текущего шага — целая часть суммы предыдущих наград на их число.
На первом шаге база равна нулю. Число наград растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def base_trace(rewards: Sequence[int]) -> List[Tuple[int, int, int]]:
    total = 0
    count = 0
    trace = []
    for reward in rewards:
        base = 0 if count == 0 else total // count
        advantage = reward - base
        total += reward
        count += 1
        trace.append((base, advantage, total // count))
    return trace


class OnlineBaseTask(BaseMathTask):
    TASK_TYPE = "online_base"
    TASK_TYPES = ["adv", "mean"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "m": 4}, 2: {"n": 3, "m": 4}, 3: {"n": 4, "m": 5},
        4: {"n": 5, "m": 5}, 5: {"n": 6, "m": 6}, 6: {"n": 7, "m": 6},
        7: {"n": 8, "m": 6}, 8: {"n": 10, "m": 7}, 9: {"n": 12, "m": 7},
        10: {"n": 14, "m": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.rewards = [random.randint(0, limit) for _ in range(self.n)]
        self.trace = base_trace(self.rewards)
        self.k = random.randint(1, self.n)
        self.adv = self.trace[self.k - 1][1]
        self.mean = self.trace[-1][2]
        self.answer = self.adv if self.task_type == "adv" else self.mean
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(reward) for reward in self.rewards)
        key = "s0" if self.task_type == "adv" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, k=self.k)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, reward=reward, base=base, adv=adv, mean=mean)
            for index, (reward, (base, adv, mean)) in enumerate(zip(self.rewards, self.trace), 1)
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
