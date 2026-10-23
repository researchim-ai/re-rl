"""RallyLeadTask — смена лидера по ходу розыгрыша.

Очко увеличивает счёт команды 1 или 2. Лидер есть, только если счёт не равный.
Смена лидера, включая переход к ничьей, считается. Число очков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def rally_trace(points: Sequence[int]) -> Tuple[int, int, List[Tuple[int, int, int, int]]]:
    scores = [0, 0]
    leader = 0
    swings = 0
    history = []
    for point in points:
        scores[point - 1] += 1
        if scores[0] == scores[1]:
            current = 0
        elif scores[0] > scores[1]:
            current = 1
        else:
            current = 2
        if current != leader:
            swings += 1
            leader = current
        history.append((scores[0], scores[1], leader, swings))
    return leader, swings, history


class RallyLeadTask(BaseMathTask):
    TASK_TYPE = "rally_lead"
    TASK_TYPES = ["leader", "swings"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.points = [random.choice((1, 2)) for _ in range(self.n)]
        self.leader, self.swings, self.history = rally_trace(self.points)
        self.answer = self.leader if self.task_type == "leader" else self.swings
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = " ".join(str(point) for point in self.points)
        key = "s0" if self.task_type == "leader" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, a=a, b=b, leader=leader, swings=swings)
            for index, (a, b, leader, swings) in enumerate(self.history, 1)
        ]
        steps.append(texts.t("s3", self.language, leader=self.leader, swings=self.swings))
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
