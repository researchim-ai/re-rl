"""BestReplyTask — поочерёдные лучшие ответы двух игроков.

Игрок выбирает действие с большей своей наградой при текущем действии соперника. При равенстве берётся номер 0.
Затем соперник так же отвечает на выбранное действие. Число ходов игрока растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Matrix = Sequence[Sequence[int]]


def reply_trace(agent: Matrix, opponent: Matrix, opp: int, rounds: int) -> List[Tuple[int, int, int, int]]:
    total = 0
    trace = []
    for _ in range(rounds):
        action = 0 if agent[0][opp] >= agent[1][opp] else 1
        payoff = agent[action][opp]
        total += payoff
        opp = 0 if opponent[0][action] >= opponent[1][action] else 1
        trace.append((action, payoff, opp, total))
    return trace


class BestReplyTask(BaseMathTask):
    TASK_TYPE = "best_reply"
    TASK_TYPES = ["total", "action"]

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
        self.agent = tuple(tuple(random.randint(-2, 3) for _ in range(2)) for _ in range(2))
        self.opponent = tuple(tuple(random.randint(-2, 3) for _ in range(2)) for _ in range(2))
        self.opp = random.randint(0, 1)
        self.trace = reply_trace(self.agent, self.opponent, self.opp, self.n)
        self.total = self.trace[-1][3]
        self.action = self.trace[-1][0]
        self.answer = self.total if self.task_type == "total" else self.action
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        agent = self._matrix(self.agent)
        opponent = self._matrix(self.opponent)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, agent=agent, opponent=opponent, opp=self.opp)

    @staticmethod
    def _matrix(matrix: Matrix) -> str:
        return ", ".join(
            f"{row} {col}:{matrix[row][col]}" for row in range(2) for col in range(2)
        )

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, action=action, payoff=payoff, opp=opp, total=total,
            )
            for index, (action, payoff, opp, total) in enumerate(self.trace, 1)
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
