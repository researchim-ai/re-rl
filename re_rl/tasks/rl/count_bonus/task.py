"""CountBonusTask — добавка за редкое посещение состояния.

Добавка равна запасу, делённому на единицу плюс число прошлых визитов, с округлением вниз.
Число визитов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Visit = Tuple[int, int]


def bonus_trace(states: int, visits: Sequence[Visit], pool: int) -> List[Tuple[int, int, int]]:
    counts = [0] * (states + 1)
    bonus_sum = 0
    score_sum = 0
    trace = []
    for state, reward in visits:
        bonus = pool // (1 + counts[state])
        counts[state] += 1
        bonus_sum += bonus
        score_sum += reward + bonus
        trace.append((bonus, bonus_sum, score_sum))
    return trace


class CountBonusTask(BaseMathTask):
    TASK_TYPE = "count_bonus"
    TASK_TYPES = ["bonus", "score"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "s": 2, "p": 4}, 2: {"n": 4, "s": 2, "p": 4},
        3: {"n": 5, "s": 2, "p": 4}, 4: {"n": 6, "s": 3, "p": 6},
        5: {"n": 7, "s": 3, "p": 6}, 6: {"n": 8, "s": 3, "p": 6},
        7: {"n": 9, "s": 3, "p": 8}, 8: {"n": 10, "s": 4, "p": 8},
        9: {"n": 12, "s": 4, "p": 8}, 10: {"n": 14, "s": 4, "p": 8},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = max(1, int(p["s"]))
        self.pool = max(1, int(p["p"]))
        self.visits = [
            (random.randint(1, self.states), random.randint(0, 4))
            for _ in range(self.n)
        ]
        self.trace = bonus_trace(self.states, self.visits, self.pool)
        _, self.bonus, self.score = self.trace[-1]
        self.answer = self.bonus if self.task_type == "bonus" else self.score
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{state}, {reward}" for state, reward in self.visits)
        key = "s0" if self.task_type == "bonus" else "s1"
        return texts.t(
            key, language, states=self.states, n=self.n, pool=self.pool, listing=listing,
        )

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, state=state, reward=reward, bonus=bonus, total=total, score=score)
            for index, ((state, reward), (bonus, total, score)) in enumerate(zip(self.visits, self.trace), 1)
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
