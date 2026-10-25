"""BeliefVoteTask — мнение меняется только за порогом.

Между порогами старое мнение сохраняется. Смена считается, когда мнение стало другим.
Число свидетельств растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def belief_trace(evidence: Sequence[int], threshold: int = 2) -> List[Tuple[int, int, int]]:
    score = 0
    belief = 0
    flips = 0
    trace = []
    for step in evidence:
        score += step
        nxt = belief
        if score >= threshold:
            nxt = 1
        elif score <= -threshold:
            nxt = 0
        if nxt != belief:
            flips += 1
            belief = nxt
        trace.append((score, belief, flips))
    return trace


class BeliefVoteTask(BaseMathTask):
    TASK_TYPE = "belief_vote"
    TASK_TYPES = ["flips", "belief"]
    THRESHOLD = 2

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
        self.evidence = [random.choice((-1, 1)) for _ in range(self.n)]
        self.trace = belief_trace(self.evidence, self.THRESHOLD)
        self.flips = self.trace[-1][2]
        self.belief = self.trace[-1][1]
        self.answer = self.flips if self.task_type == "flips" else self.belief
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(str(step) for step in self.evidence)
        key = "s0" if self.task_type == "flips" else "s1"
        return texts.t(key, language, n=self.n, evidence=shown, threshold=self.THRESHOLD)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, step=step, score=score, belief=belief, flips=flips)
            for index, (step, (score, belief, flips)) in enumerate(zip(self.evidence, self.trace), 1)
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
