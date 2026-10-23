"""UcbBanditTask — целочисленный выбор руки.

Сначала руки берутся по номерам. Затем сравнивается
(сумма наград руки + число уже сделанных ходов) / число её ходов.
Число ходов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.ml._exact import fmt_fraction

Column = Sequence[int]


def ucb_trace(columns: Sequence[Column]) -> List[Tuple[int, int, int, List[int], List[Fraction]]]:
    arms = len(columns)
    sums = [0] * arms
    counts = [0] * arms
    trace = []
    total = 0
    for pull in range(len(columns[0])):
        if pull < arms:
            arm = pull
            scores: List[Fraction] = []
        else:
            arm = 0
            best = None
            scores = []
            for candidate in range(arms):
                score = Fraction(sums[candidate] + pull, counts[candidate])
                scores.append(score)
                if best is None or score > best:
                    best = score
                    arm = candidate
        reward = columns[arm][counts[arm]]
        sums[arm] += reward
        counts[arm] += 1
        total += reward
        trace.append((arm + 1, reward, total, list(counts), scores))
    return trace


class UcbBanditTask(BaseMathTask):
    TASK_TYPE = "ucb_bandit"
    TASK_TYPES = ["reward", "arm"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "m": 3}, 2: {"n": 4, "m": 3}, 3: {"n": 5, "m": 4},
        4: {"n": 6, "m": 4}, 5: {"n": 7, "m": 4}, 6: {"n": 8, "m": 5},
        7: {"n": 9, "m": 5}, 8: {"n": 10, "m": 5}, 9: {"n": 11, "m": 6},
        10: {"n": 12, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.arms = 3
        limit = max(1, int(p["m"]))
        self.columns = [
            [random.randint(0, limit) for _ in range(self.n)]
            for _ in range(self.arms)
        ]
        self.trace = ucb_trace(self.columns)
        _, _, self.reward, self.counts, _scores = self.trace[-1]
        best = max(self.counts)
        self.arm = min(index for index, count in enumerate(self.counts) if count == best) + 1
        self.answer = self.reward if self.task_type == "reward" else self.arm
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(
            f"{arm}: " + ", ".join(str(reward) for reward in column)
            for arm, column in enumerate(self.columns, 1)
        )
        key = "s0" if self.task_type == "reward" else "s1"
        return texts.t(key, language, arms=self.arms, n=self.n, listing=listing)

    def solve(self):
        steps = []
        for index, (arm, reward, total, counts, scores) in enumerate(self.trace, 1):
            shown_counts = ", ".join(str(count) for count in counts)
            shown_scores = (
                texts.t("s3", self.language) if not scores
                else ", ".join(fmt_fraction(score) for score in scores)
            )
            steps.append(texts.t(
                "s2", self.language, i=index, arm=arm, reward=reward,
                total=total, counts=shown_counts, scores=shown_scores,
            ))
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
