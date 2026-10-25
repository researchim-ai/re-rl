"""FirstToTask — кто первым наберёт нужное число успехов.

Очки после победы больше не растут. Если порог не взят, победителя нет.
Число попыток растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def firstto_trace(goal: int, trials: Sequence[int]) -> List[Tuple[int, int, int]]:
    scores = [0, 0]
    winner = 0
    trial = 0
    trace = []
    for index, who in enumerate(trials, 1):
        if winner == 0:
            scores[who - 1] += 1
            if scores[who - 1] >= goal:
                winner = who
                trial = index
        trace.append((scores[0], winner, trial))
    return trace


class FirstToTask(BaseMathTask):
    TASK_TYPE = "first_to"
    TASK_TYPES = ["winner", "trial"]
    GOAL = 2

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
        self.trials = [random.randint(1, 2) for _ in range(self.n)]
        self.trace = firstto_trace(self.GOAL, self.trials)
        self.winner = self.trace[-1][1]
        self.trial = self.trace[-1][2]
        self.answer = self.winner if self.task_type == "winner" else self.trial
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(trial) for trial in self.trials)
        key = "s0" if self.task_type == "winner" else "s1"
        return texts.t(key, language, n=self.n, goal=self.GOAL, trials=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, who=who, score=score, winner=winner, trial=trial)
            for index, (who, (score, winner, trial)) in enumerate(zip(self.trials, self.trace), 1)
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
