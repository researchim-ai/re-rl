"""ArmRateTask — какая рука впереди по доле успехов.

Рука без попыток не лидирует. Если попытки есть у обеих, сравниваются произведения успехов на число попыток другой руки.
Число попыток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pull = Tuple[int, int]


def arm_trace(pulls: Sequence[Pull]) -> List[Tuple[int, int, int, int, int]]:
    success = [0, 0, 0]
    count = [0, 0, 0]
    trace = []
    for arm, reward in pulls:
        success[arm] += reward
        count[arm] += 1
        if count[1] == 0:
            leader = 2
        elif count[2] == 0:
            leader = 1
        else:
            left = success[1] * count[2]
            right = success[2] * count[1]
            if left > right:
                leader = 1
            elif right > left:
                leader = 2
            else:
                leader = 0
        trace.append((leader, success[1], success[2], count[1], count[2]))
    return trace


class ArmRateTask(BaseMathTask):
    TASK_TYPE = "arm_rate"
    TASK_TYPES = ["leader", "hits"]

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
        self.pulls = [(random.randint(1, 2), random.randint(0, 1)) for _ in range(self.n)]
        self.trace = arm_trace(self.pulls)
        self.leader = self.trace[-1][0]
        self.hits = self.trace[-1][1]
        self.answer = self.leader if self.task_type == "leader" else self.hits
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(f"{arm} {reward}" for arm, reward in self.pulls)
        key = "s0" if self.task_type == "leader" else "s1"
        return texts.t(key, language, n=self.n, pulls=shown)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, arm=arm, reward=reward, leader=leader,
                s1=s1, s2=s2, c1=c1, c2=c2,
            )
            for index, ((arm, reward), (leader, s1, s2, c1, c2)) in enumerate(zip(self.pulls, self.trace), 1)
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
