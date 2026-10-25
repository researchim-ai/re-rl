"""CausalPickTask — выбор ключа только из уже виденных позиций.

На позиции i доступны оценки 1..i. Берётся наибольшая, при равенстве остаётся более ранняя.
Число позиций растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def prefix_choice(scores: Sequence[int]) -> List[Tuple[int, int, int]]:
    best_at = 0
    best: Optional[int] = None
    lookbacks = 0
    trace = []
    for index, score in enumerate(scores, 1):
        if best is None or score > best:
            best = score
            best_at = index
        if best_at != index:
            lookbacks += 1
        trace.append((best_at, best, lookbacks))
    return trace


class CausalPickTask(BaseMathTask):
    TASK_TYPE = "causal_pick"
    TASK_TYPES = ["chosen", "look"]

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
        self.scores = [random.randint(0, 9) for _ in range(self.n)]
        self.trace = prefix_choice(self.scores)
        self.chosen = self.trace[-1][0]
        self.look = self.trace[-1][2]
        self.answer = self.chosen if self.task_type == "chosen" else self.look
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(score) for score in self.scores)
        key = "s0" if self.task_type == "chosen" else "s1"
        return texts.t(key, language, n=self.n, scores=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, score=score, chosen=chosen, best=best, look=look)
            for index, (score, (chosen, best, look)) in enumerate(zip(self.scores, self.trace), 1)
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
